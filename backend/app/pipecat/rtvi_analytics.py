"""
RTVI Analytics Observer
Captures real-time voice interaction events and stores them in Supabase
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from .models import RTVIEvent, CallMetrics, CallOutcome, ConversationState

logger = logging.getLogger(__name__)


class RTVIAnalyticsObserver:
    """
    Observer class that captures RTVI events during voice calls
    and stores analytics data in real-time
    """
    
    def __init__(self, call_id: str, supabase_client):
        self.call_id = call_id
        self.supabase_client = supabase_client
        self.start_time = datetime.utcnow()
        self.events: List[RTVIEvent] = []
        self.metrics = CallMetrics(
            call_id=call_id,
            start_time=self.start_time
        )
        self.conversation_state: Optional[ConversationState] = None
        
        # Analytics tracking
        self.interruption_count = 0
        self.sentiment_shifts = 0
        self.tokens_used = 0
        self.last_sentiment = "neutral"
        
        logger.info(f"RTVIAnalyticsObserver initialized for call: {call_id}")
    
    async def process_frame(self, frame) -> None:
        """Process incoming PIPECAT frames and extract analytics"""
        try:
            frame_type = type(frame).__name__
            
            # Track user interruptions
            if frame_type == "UserStartedSpeakingFrame":
                await self._track_interruption()
            
            # Track transcription for sentiment analysis
            elif frame_type == "TranscriptionFrame":
                await self._track_transcription(frame)
            
            # Track LLM token usage
            elif frame_type == "LLMMessagesFrame":
                await self._track_llm_usage(frame)
            
            # Track conversation state changes
            elif frame_type == "SystemFrame":
                await self._track_system_event(frame)
                
        except Exception as e:
            logger.error(f"Error processing frame in analytics observer: {e}")
    
    async def _track_interruption(self) -> None:
        """Track when user interrupts the agent"""
        self.interruption_count += 1
        self.metrics.interruption_count += 1
        
        event = RTVIEvent(
            event_id=str(uuid.uuid4()),
            call_id=self.call_id,
            event_type="user_interruption",
            timestamp=datetime.utcnow(),
            data={
                "interruption_number": self.interruption_count,
                "call_duration_seconds": (datetime.utcnow() - self.start_time).total_seconds()
            }
        )
        
        await self._store_event(event)
        logger.debug(f"Tracked interruption #{self.interruption_count} for call {self.call_id}")
    
    async def _track_transcription(self, frame) -> None:
        """Analyze transcription for sentiment and keywords"""
        try:
            if hasattr(frame, 'text'):
                text = frame.text.lower()
                
                # Simple sentiment analysis based on keywords
                current_sentiment = self._analyze_sentiment(text)
                
                if current_sentiment != self.last_sentiment:
                    self.sentiment_shifts += 1
                    self.metrics.sentiment_shifts += 1
                    
                    event = RTVIEvent(
                        event_id=str(uuid.uuid4()),
                        call_id=self.call_id,
                        event_type="sentiment_shift",
                        timestamp=datetime.utcnow(),
                        data={
                            "previous_sentiment": self.last_sentiment,
                            "new_sentiment": current_sentiment,
                            "transcription": frame.text,
                            "shift_number": self.sentiment_shifts
                        }
                    )
                    
                    await self._store_event(event)
                    self.last_sentiment = current_sentiment
                
                # Check for emergency keywords
                if self._detect_emergency_keywords(text):
                    event = RTVIEvent(
                        event_id=str(uuid.uuid4()),
                        call_id=self.call_id,
                        event_type="emergency_keyword_detected",
                        timestamp=datetime.utcnow(),
                        data={
                            "transcription": frame.text,
                            "keywords_found": self._extract_emergency_keywords(text)
                        }
                    )
                    
                    await self._store_event(event)
                
        except Exception as e:
            logger.error(f"Error tracking transcription: {e}")
    
    async def _track_llm_usage(self, frame) -> None:
        """Track LLM token usage"""
        try:
            # Extract token usage from LLM response if available
            if hasattr(frame, 'usage') and frame.usage:
                tokens = frame.usage.get('total_tokens', 0)
                self.tokens_used += tokens
                self.metrics.total_tokens += tokens
                
                event = RTVIEvent(
                    event_id=str(uuid.uuid4()),
                    call_id=self.call_id,
                    event_type="token_usage",
                    timestamp=datetime.utcnow(),
                    data={
                        "tokens_used": tokens,
                        "cumulative_tokens": self.tokens_used,
                        "prompt_tokens": frame.usage.get('prompt_tokens', 0),
                        "completion_tokens": frame.usage.get('completion_tokens', 0)
                    }
                )
                
                await self._store_event(event)
                
        except Exception as e:
            logger.error(f"Error tracking LLM usage: {e}")
    
    async def _track_system_event(self, frame) -> None:
        """Track system events like call outcomes"""
        try:
            if hasattr(frame, 'data') and isinstance(frame.data, dict):
                event_type = frame.data.get('event_type')
                
                if event_type == "call_outcome_determined":
                    outcome = frame.data.get('outcome')
                    self.metrics.final_outcome = outcome
                    
                    event = RTVIEvent(
                        event_id=str(uuid.uuid4()),
                        call_id=self.call_id,
                        event_type="call_outcome",
                        timestamp=datetime.utcnow(),
                        data={
                            "outcome": outcome,
                            "call_duration_seconds": (datetime.utcnow() - self.start_time).total_seconds()
                        }
                    )
                    
                    await self._store_event(event)
                
        except Exception as e:
            logger.error(f"Error tracking system event: {e}")
    
    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis based on keywords"""
        positive_words = ['good', 'great', 'fine', 'okay', 'safe', 'no problem', 'excellent', 'perfect']
        negative_words = ['emergency', 'problem', 'trouble', 'accident', 'breakdown', 'stuck', 'delayed', 'urgent']
        neutral_words = ['driving', 'location', 'arrived', 'unloading', 'route']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > 0:
            return "positive"
        else:
            return "neutral"
    
    def _detect_emergency_keywords(self, text: str) -> bool:
        """Detect emergency keywords in transcription"""
        emergency_keywords = [
            'emergency', 'accident', 'breakdown', 'medical', 'help', 'urgent',
            'blowout', 'crash', 'collision', 'injury', 'hurt', 'stuck', 'disabled',
            'broke down', 'can\'t move', 'need help', 'pulled over', 'on fire'
        ]
        
        return any(keyword in text for keyword in emergency_keywords)
    
    def _extract_emergency_keywords(self, text: str) -> List[str]:
        """Extract which emergency keywords were found"""
        emergency_keywords = [
            'emergency', 'accident', 'breakdown', 'medical', 'help', 'urgent',
            'blowout', 'crash', 'collision', 'injury', 'hurt', 'stuck', 'disabled',
            'broke down', 'can\'t move', 'need help', 'pulled over', 'on fire'
        ]
        
        found_keywords = [keyword for keyword in emergency_keywords if keyword in text]
        return found_keywords
    
    async def _store_event(self, event: RTVIEvent) -> None:
        """Store event in Supabase"""
        try:
            await self.supabase_client.create_rtvi_event({
                "event_id": event.event_id,
                "call_id": event.call_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "data": event.data
            })
            
            self.events.append(event)
            
        except Exception as e:
            logger.error(f"Error storing RTVI event: {e}")
    
    async def update_conversation_state(self, state: ConversationState) -> None:
        """Update the current conversation state"""
        self.conversation_state = state
        
        # Update metrics
        self.metrics.interruption_count = state.interruption_count
        self.metrics.total_tokens = state.tokens_used
        
        # Store state change event
        event = RTVIEvent(
            event_id=str(uuid.uuid4()),
            call_id=self.call_id,
            event_type="conversation_state_change",
            timestamp=datetime.utcnow(),
            data={
                "phase": state.phase,
                "emergency_detected": state.emergency_detected,
                "clarification_attempts": state.clarification_attempts,
                "scenario_type": state.scenario_type
            }
        )
        
        await self._store_event(event)
    
    async def finalize_call(self) -> CallMetrics:
        """Finalize call analytics and store final metrics"""
        self.metrics.end_time = datetime.utcnow()
        self.metrics.duration_seconds = (self.metrics.end_time - self.metrics.start_time).total_seconds()
        
        # Store final call metrics
        try:
            await self.supabase_client.create_call_metrics({
                "call_id": self.metrics.call_id,
                "start_time": self.metrics.start_time.isoformat(),
                "end_time": self.metrics.end_time.isoformat(),
                "duration_seconds": self.metrics.duration_seconds,
                "total_tokens": self.metrics.total_tokens,
                "interruption_count": self.metrics.interruption_count,
                "sentiment_shifts": self.metrics.sentiment_shifts,
                "final_outcome": self.metrics.final_outcome
            })
            
            logger.info(f"Finalized analytics for call {self.call_id}: "
                       f"Duration: {self.metrics.duration_seconds:.1f}s, "
                       f"Tokens: {self.metrics.total_tokens}, "
                       f"Interruptions: {self.metrics.interruption_count}")
            
        except Exception as e:
            logger.error(f"Error storing final call metrics: {e}")
        
        return self.metrics
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current call metrics"""
        current_duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "call_id": self.call_id,
            "duration_seconds": current_duration,
            "total_tokens": self.metrics.total_tokens,
            "interruption_count": self.metrics.interruption_count,
            "sentiment_shifts": self.metrics.sentiment_shifts,
            "events_captured": len(self.events),
            "final_outcome": self.metrics.final_outcome
        }