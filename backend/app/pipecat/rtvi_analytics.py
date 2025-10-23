
import asyncio
import logging
import json
import re
from typing import Dict, Any, Optional, List, Tuple, Set
from datetime import datetime, timedelta
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass, field

from .models import RTVIEvent, CallMetrics, CallOutcome, ConversationState
from .voice_quality_assessor import VoiceQualityAssessor, OverallQualityAssessment

logger = logging.getLogger(__name__)


@dataclass
class ConversationQuality:
    """Advanced conversation quality metrics"""
    clarity_score: float = 0.0
    engagement_score: float = 0.0
    efficiency_score: float = 0.0
    professional_score: float = 0.0
    completion_score: float = 0.0
    overall_score: float = 0.0
    
    
@dataclass
class VoiceMetrics:
    """Voice quality and pattern metrics"""
    audio_quality_score: float = 0.0
    speech_rate_wpm: float = 0.0
    pause_duration_avg: float = 0.0
    volume_consistency: float = 0.0
    interruption_pattern_score: float = 0.0
    

@dataclass
class SentimentTimeline:
    """Tracks sentiment changes over time"""
    timestamps: List[datetime] = field(default_factory=list)
    sentiments: List[str] = field(default_factory=list)
    confidence_scores: List[float] = field(default_factory=list)
    
    def add_sentiment(self, sentiment: str, confidence: float):
        self.timestamps.append(datetime.utcnow())
        self.sentiments.append(sentiment)
        self.confidence_scores.append(confidence)


@dataclass
class CallPredictions:
    """AI-powered call predictions"""
    expected_duration: float = 0.0
    likely_outcome: str = "unknown"
    emergency_probability: float = 0.0
    completion_probability: float = 0.0
    driver_mood_prediction: str = "neutral"


class EnhancedRTVIAnalyticsObserver:
    """
    Enhanced RTVI Analytics Observer with ML-driven insights and real-time quality assessment
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
        self.quality_metrics = ConversationQuality()
        self.voice_metrics = VoiceMetrics()
        self.sentiment_timeline = SentimentTimeline()
        self.predictions = CallPredictions()
        
        self.voice_quality_assessor = VoiceQualityAssessor(call_id)
        self.quality_assessment: Optional[OverallQualityAssessment] = None
        
        self.interruption_count = 0
        self.sentiment_shifts = 0
        self.tokens_used = 0
        self.last_sentiment = "neutral"
        self.conversation_turns = 0
        self.dead_air_segments = 0
        self.clarification_requests = 0
        self.topic_changes = 0
        
        self.recent_transcripts = deque(maxlen=10)
        self.response_times = deque(maxlen=20)
        self.interruption_timestamps = deque(maxlen=50)
        self.keyword_frequencies = defaultdict(int)
        
        self.emergency_indicators: Set[str] = set()
        self.professionalism_markers = {
            'positive': ['please', 'thank you', 'appreciate', 'understand', 'certainly'],
            'negative': ['damn', 'hell', 'shit', 'stupid', 'idiot']
        }
        
        self.conversation_phases = ['greeting', 'information_gathering', 'problem_solving', 'conclusion']
        self.current_phase = 'greeting'
        self.phase_timestamps = {}
        
        logger.info(f"Enhanced RTVI Analytics Observer initialized for call: {call_id}")
    
    async def process_frame(self, frame) -> None:
        """Process PIPECAT frames with enhanced analytics"""
        try:
            frame_type = type(frame).__name__
            timestamp = datetime.utcnow()
            
            if frame_type == "UserStartedSpeakingFrame":
                await self._track_user_speech_start(timestamp)
            elif frame_type == "UserStoppedSpeakingFrame":
                await self._track_user_speech_end(timestamp)
            elif frame_type == "TranscriptionFrame":
                await self._enhanced_transcription_analysis(frame, timestamp)
            elif frame_type == "LLMMessagesFrame":
                await self._enhanced_llm_analysis(frame, timestamp)
            elif frame_type == "SystemFrame":
                await self._track_system_event(frame, timestamp)
            elif frame_type == "AudioRawFrame":
                await self._analyze_audio_quality(frame, timestamp)
            
            await self._update_conversation_quality()
            await self._update_predictions()
            
        except Exception as e:
            logger.error(f"Error in enhanced analytics processing: {e}")
    
    async def _track_user_speech_start(self, timestamp: datetime) -> None:
        """Enhanced user speech start tracking"""
        self.interruption_count += 1
        self.interruption_timestamps.append(timestamp)
        
        if len(self.interruption_timestamps) >= 2:
            time_since_last = (timestamp - self.interruption_timestamps[-2]).total_seconds()
            self.voice_metrics.interruption_pattern_score = self._calculate_interruption_pattern()
        
        event = RTVIEvent(
            event_id=str(uuid.uuid4()),
            call_id=self.call_id,
            event_type="user_speech_start",
            timestamp=timestamp,
            data={
                "interruption_number": self.interruption_count,
                "call_duration_seconds": (timestamp - self.start_time).total_seconds(),
                "interruption_pattern_score": self.voice_metrics.interruption_pattern_score
            }
        )
        
        await self._store_event(event)
    
    async def _track_user_speech_end(self, timestamp: datetime) -> None:
        """Track when user stops speaking"""
        event = RTVIEvent(
            event_id=str(uuid.uuid4()),
            call_id=self.call_id,
            event_type="user_speech_end",
            timestamp=timestamp,
            data={
                "call_duration_seconds": (timestamp - self.start_time).total_seconds()
            }
        )
        
        await self._store_event(event)
    
    async def _enhanced_transcription_analysis(self, frame, timestamp: datetime) -> None:
        """Advanced transcription analysis with NLP insights"""
        try:
            if not hasattr(frame, 'text') or not frame.text:
                return
                
            text = frame.text.lower().strip()
            self.recent_transcripts.append(text)
            self.conversation_turns += 1
            
            sentiment_data = self._advanced_sentiment_analysis(text)
            current_sentiment = sentiment_data['sentiment']
            confidence = sentiment_data['confidence']
            
            self.sentiment_timeline.add_sentiment(current_sentiment, confidence)
            
            if current_sentiment != self.last_sentiment:
                self.sentiment_shifts += 1
                self.metrics.sentiment_shifts += 1
                
                event = RTVIEvent(
                    event_id=str(uuid.uuid4()),
                    call_id=self.call_id,
                    event_type="sentiment_shift",
                    timestamp=timestamp,
                    data={
                        "previous_sentiment": self.last_sentiment,
                        "new_sentiment": current_sentiment,
                        "confidence_score": confidence,
                        "transcription": frame.text,
                        "shift_number": self.sentiment_shifts,
                        "emotional_intensity": sentiment_data['intensity']
                    }
                )
                
                await self._store_event(event)
                self.last_sentiment = current_sentiment
            
            await self._analyze_keywords_and_topics(text, timestamp)
            
            emergency_data = self._enhanced_emergency_detection(text)
            if emergency_data['detected']:
                event = RTVIEvent(
                    event_id=str(uuid.uuid4()),
                    call_id=self.call_id,
                    event_type="emergency_detected",
                    timestamp=timestamp,
                    data={
                        "transcription": frame.text,
                        "emergency_keywords": emergency_data['keywords'],
                        "confidence_score": emergency_data['confidence'],
                        "emergency_type": emergency_data['type'],
                        "severity_level": emergency_data['severity']
                    }
                )
                
                await self._store_event(event)
            
            await self._analyze_conversation_flow(text, timestamp)
            
        except Exception as e:
            logger.error(f"Error in enhanced transcription analysis: {e}")
    
    async def _enhanced_llm_analysis(self, frame, timestamp: datetime) -> None:
        """Enhanced LLM response analysis"""
        try:
            if hasattr(frame, 'usage') and frame.usage:
                tokens = frame.usage.get('total_tokens', 0)
                self.tokens_used += tokens
                self.metrics.total_tokens += tokens
                
                efficiency_score = self._calculate_response_efficiency(tokens, frame)
                
                event = RTVIEvent(
                    event_id=str(uuid.uuid4()),
                    call_id=self.call_id,
                    event_type="llm_response",
                    timestamp=timestamp,
                    data={
                        "tokens_used": tokens,
                        "cumulative_tokens": self.tokens_used,
                        "prompt_tokens": frame.usage.get('prompt_tokens', 0),
                        "completion_tokens": frame.usage.get('completion_tokens', 0),
                        "efficiency_score": efficiency_score,
                        "response_quality": self._assess_response_quality(frame)
                    }
                )
                
                await self._store_event(event)
                
        except Exception as e:
            logger.error(f"Error in enhanced LLM analysis: {e}")
    
    async def _analyze_audio_quality(self, frame, timestamp: datetime) -> None:
        """Analyze audio quality metrics with voice quality assessor integration"""
        try:
            if hasattr(frame, 'audio_data'):
                await self.voice_quality_assessor.process_audio_sample(frame.audio_data, timestamp)
                
                quality_score = await self._get_current_audio_quality()
                self.voice_metrics.audio_quality_score = quality_score
                
                if quality_score < 0.5:  
                    event = RTVIEvent(
                        event_id=str(uuid.uuid4()),
                        call_id=self.call_id,
                        event_type="audio_quality_warning",
                        timestamp=timestamp,
                        data={
                            "quality_score": quality_score,
                            "quality_level": "poor" if quality_score < 0.3 else "fair",
                            "assessor_data": self.voice_quality_assessor.assessment.audio_metrics.__dict__
                        }
                    )
                    
                    await self._store_event(event)
                    
        except Exception as e:
            logger.error(f"Error in enhanced audio quality analysis: {e}")
    
    async def _get_current_audio_quality(self) -> float:
        """Get current audio quality score from voice quality assessor"""
        try:
            audio_metrics = self.voice_quality_assessor.assessment.audio_metrics
            return (
                audio_metrics.clarity_score * 0.4 +
                (1 - audio_metrics.background_noise_level) * 0.3 +
                audio_metrics.volume_consistency * 0.3
            )
        except:
            return 0.8  # Default quality score
    
    def _advanced_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Advanced sentiment analysis with confidence and intensity"""
        positive_words = {
            'great': 2, 'excellent': 3, 'perfect': 3, 'good': 1, 'fine': 1,
            'okay': 0.5, 'safe': 1, 'no problem': 2, 'thank you': 1
        }
        
        negative_words = {
            'emergency': 3, 'accident': 3, 'problem': 2, 'trouble': 2,
            'breakdown': 3, 'stuck': 2, 'delayed': 1, 'urgent': 2,
            'frustrated': 2, 'angry': 2, 'upset': 2
        }
        
        neutral_words = {
            'driving': 0, 'location': 0, 'arrived': 0, 'unloading': 0,
            'route': 0, 'mile': 0, 'highway': 0
        }
        
        positive_score = sum(positive_words.get(word, 0) for word in text.split())
        negative_score = sum(negative_words.get(word, 0) for word in text.split())
        
        total_words = len(text.split())
        
        if negative_score > positive_score:
            sentiment = "negative"
            intensity = min(negative_score / total_words, 1.0)
        elif positive_score > 0:
            sentiment = "positive"
            intensity = min(positive_score / total_words, 1.0)
        else:
            sentiment = "neutral"
            intensity = 0.5
            
        confidence = min((abs(positive_score - negative_score) + 1) / 10, 1.0)
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'intensity': intensity,
            'positive_score': positive_score,
            'negative_score': negative_score
        }
    
    def _enhanced_emergency_detection(self, text: str) -> Dict[str, Any]:
        """Enhanced emergency detection with type classification"""
        emergency_patterns = {
            'accident': ['accident', 'crash', 'collision', 'hit', 'smash'],
            'medical': ['medical', 'injury', 'hurt', 'pain', 'hospital', 'ambulance'],
            'mechanical': ['breakdown', 'broke down', 'engine', 'tire', 'blowout', 'mechanical'],
            'safety': ['emergency', 'help', 'urgent', 'dangerous', 'unsafe'],
            'stuck': ['stuck', 'disabled', 'can\'t move', 'stranded']
        }
        
        detected_keywords = []
        emergency_type = 'unknown'
        severity_score = 0
        
        for etype, keywords in emergency_patterns.items():
            for keyword in keywords:
                if keyword in text:
                    detected_keywords.append(keyword)
                    emergency_type = etype
                    severity_score += len(keyword.split())
        
        detected = len(detected_keywords) > 0
        confidence = min(severity_score / 10, 1.0) if detected else 0.0
        
        severity_level = 'low'
        if severity_score >= 5:
            severity_level = 'high'
        elif severity_score >= 3:
            severity_level = 'medium'
            
        return {
            'detected': detected,
            'keywords': detected_keywords,
            'confidence': confidence,
            'type': emergency_type,
            'severity': severity_level
        }
    
    async def _analyze_keywords_and_topics(self, text: str, timestamp: datetime) -> None:
        """Analyze keywords and track topic changes"""
        logistics_keywords = [
            'eta', 'arrival', 'delivery', 'pickup', 'load', 'unload',
            'highway', 'mile', 'exit', 'dock', 'trailer', 'dispatch'
        ]
        
        found_keywords = [kw for kw in logistics_keywords if kw in text]
        
        for keyword in found_keywords:
            self.keyword_frequencies[keyword] += 1
        
        if found_keywords:
            event = RTVIEvent(
                event_id=str(uuid.uuid4()),
                call_id=self.call_id,
                event_type="keywords_detected",
                timestamp=timestamp,
                data={
                    "keywords": found_keywords,
                    "keyword_frequencies": dict(self.keyword_frequencies)
                }
            )
            
            await self._store_event(event)
    
    async def _analyze_conversation_flow(self, text: str, timestamp: datetime) -> None:
        """Analyze conversation flow and phase transitions"""
        phase_indicators = {
            'greeting': ['hello', 'hi', 'good morning', 'this is', 'calling'],
            'information_gathering': ['where', 'when', 'what', 'how', 'status', 'location'],
            'problem_solving': ['problem', 'issue', 'help', 'solution', 'fix'],
            'conclusion': ['thank', 'bye', 'goodbye', 'complete', 'done', 'finished']
        }
        
        for phase, indicators in phase_indicators.items():
            if any(indicator in text for indicator in indicators):
                if phase != self.current_phase:
                    self.phase_timestamps[phase] = timestamp
                    
                    event = RTVIEvent(
                        event_id=str(uuid.uuid4()),
                        call_id=self.call_id,
                        event_type="conversation_phase_change",
                        timestamp=timestamp,
                        data={
                            "previous_phase": self.current_phase,
                            "new_phase": phase,
                            "phase_duration": (timestamp - self.phase_timestamps.get(self.current_phase, self.start_time)).total_seconds()
                        }
                    )
                    
                    await self._store_event(event)
                    self.current_phase = phase
                break
    
    def _calculate_interruption_pattern(self) -> float:
        """Calculate interruption pattern score"""
        if len(self.interruption_timestamps) < 2:
            return 1.0
            
        intervals = []
        for i in range(1, len(self.interruption_timestamps)):
            interval = (self.interruption_timestamps[i] - self.interruption_timestamps[i-1]).total_seconds()
            intervals.append(interval)
        
        avg_interval = sum(intervals) / len(intervals)
        
        if avg_interval < 5:
            return 0.3
        elif avg_interval > 30:
            return 1.0
        else:
            return 0.7
    
    def _calculate_response_efficiency(self, tokens: int, frame) -> float:
        """Calculate LLM response efficiency"""
        if tokens == 0:
            return 0.0
            
        if tokens < 100:
            return 1.0 
        elif tokens < 200:
            return 0.8
        elif tokens < 300:
            return 0.6
        else:
            return 0.4 
    
    def _assess_response_quality(self, frame) -> str:
        """Assess quality of LLM response"""
        if hasattr(frame, 'messages') and frame.messages:
            return "good"
        return "unknown"
    
    def _calculate_audio_quality(self, audio_data: bytes) -> float:
        """Calculate audio quality score"""
        if len(audio_data) < 1000:
            return 0.3 
        return 0.8  
    
    async def _update_conversation_quality(self) -> None:
        """Update conversation quality metrics"""
        self.quality_metrics.clarity_score = self._calculate_clarity_score()
        self.quality_metrics.engagement_score = self._calculate_engagement_score()
        self.quality_metrics.efficiency_score = self._calculate_efficiency_score()
        self.quality_metrics.professional_score = self._calculate_professional_score()
        self.quality_metrics.completion_score = self._calculate_completion_score()
        
        self.quality_metrics.overall_score = (
            self.quality_metrics.clarity_score * 0.25 +
            self.quality_metrics.engagement_score * 0.2 +
            self.quality_metrics.efficiency_score * 0.2 +
            self.quality_metrics.professional_score * 0.2 +
            self.quality_metrics.completion_score * 0.15
        )
    
    async def _update_predictions(self) -> None:
        """Update AI predictions about the call"""
        call_duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if self.conversation_turns > 5:
            self.predictions.expected_duration = call_duration * 1.5
        else:
            self.predictions.expected_duration = 180  
        
        if self.emergency_indicators:
            self.predictions.likely_outcome = "Emergency Escalation"
            self.predictions.emergency_probability = 0.9
        elif self.conversation_turns > 10:
            self.predictions.likely_outcome = "In-Transit Update"
            self.predictions.completion_probability = 0.8
        else:
            self.predictions.likely_outcome = "Information Gathering"
            self.predictions.completion_probability = 0.6
    
    def _calculate_clarity_score(self) -> float:
        """Calculate conversation clarity score"""
        if self.clarification_requests > 3:
            return 0.4
        elif self.clarification_requests > 1:
            return 0.7
        else:
            return 1.0
    
    def _calculate_engagement_score(self) -> float:
        """Calculate engagement score"""
        if self.conversation_turns < 3:
            return 0.3
        elif self.conversation_turns > 15:
            return 0.6
        else:
            return 1.0
    
    def _calculate_efficiency_score(self) -> float:
        """Calculate efficiency score"""
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        if duration > 600:  
            return 0.4
        elif duration > 300:  
            return 0.7
        else:
            return 1.0
    
    def _calculate_professional_score(self) -> float:
        """Calculate professionalism score"""
        recent_text = ' '.join(self.recent_transcripts)
        
        positive_count = sum(1 for word in self.professionalism_markers['positive'] if word in recent_text)
        negative_count = sum(1 for word in self.professionalism_markers['negative'] if word in recent_text)
        
        if negative_count > 0:
            return 0.3
        elif positive_count > 2:
            return 1.0
        else:
            return 0.8
    
    def _calculate_completion_score(self) -> float:
        """Calculate task completion score"""
        if self.current_phase == 'conclusion':
            return 1.0
        elif self.current_phase == 'problem_solving':
            return 0.7
        elif self.current_phase == 'information_gathering':
            return 0.5
        else:
            return 0.2
    
    
    async def _store_event(self, event: RTVIEvent) -> None:
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
            logger.error(f"Error storing enhanced RTVI event: {e}")
    
    async def update_conversation_state(self, state: ConversationState) -> None:
        """Update the current conversation state with enhanced tracking"""
        self.conversation_state = state
        
        # Update metrics
        self.metrics.interruption_count = state.interruption_count
        self.metrics.total_tokens = state.tokens_used
        
        event = RTVIEvent(
            event_id=str(uuid.uuid4()),
            call_id=self.call_id,
            event_type="conversation_state_change",
            timestamp=datetime.utcnow(),
            data={
                "phase": state.phase,
                "emergency_detected": state.emergency_detected,
                "clarification_attempts": state.clarification_attempts,
                "scenario_type": state.scenario_type,
                "quality_metrics": {
                    "overall_score": self.quality_metrics.overall_score,
                    "clarity_score": self.quality_metrics.clarity_score,
                    "engagement_score": self.quality_metrics.engagement_score,
                    "efficiency_score": self.quality_metrics.efficiency_score,
                    "professional_score": self.quality_metrics.professional_score
                },
                "predictions": {
                    "expected_duration": self.predictions.expected_duration,
                    "likely_outcome": self.predictions.likely_outcome,
                    "emergency_probability": self.predictions.emergency_probability,
                    "completion_probability": self.predictions.completion_probability
                }
            }
        )
        
        await self._store_event(event)
    
    async def finalize_call(self) -> CallMetrics:
        """Finalize call analytics with comprehensive metrics"""
        self.metrics.end_time = datetime.utcnow()
        self.metrics.duration_seconds = (self.metrics.end_time - self.metrics.start_time).total_seconds()
        
        # Calculate final quality scores
        await self._update_conversation_quality()
        
        # Store comprehensive final call metrics
        try:
            final_data = {
                "call_id": self.metrics.call_id,
                "start_time": self.metrics.start_time.isoformat(),
                "end_time": self.metrics.end_time.isoformat(),
                "duration_seconds": self.metrics.duration_seconds,
                "total_tokens": self.metrics.total_tokens,
                "interruption_count": self.metrics.interruption_count,
                "sentiment_shifts": self.metrics.sentiment_shifts,
                "final_outcome": self.metrics.final_outcome,
                "conversation_turns": self.conversation_turns,
                "quality_scores": {
                    "overall": self.quality_metrics.overall_score,
                    "clarity": self.quality_metrics.clarity_score,
                    "engagement": self.quality_metrics.engagement_score,
                    "efficiency": self.quality_metrics.efficiency_score,
                    "professional": self.quality_metrics.professional_score,
                    "completion": self.quality_metrics.completion_score
                },
                "voice_metrics": {
                    "audio_quality": self.voice_metrics.audio_quality_score,
                    "interruption_pattern": self.voice_metrics.interruption_pattern_score
                },
                "conversation_flow": {
                    "current_phase": self.current_phase,
                    "phase_transitions": len(self.phase_timestamps),
                    "topic_changes": self.topic_changes
                },
                "keyword_analysis": dict(self.keyword_frequencies),
                "sentiment_timeline": {
                    "total_shifts": self.sentiment_shifts,
                    "final_sentiment": self.last_sentiment,
                    "sentiment_distribution": self._get_sentiment_distribution()
                }
            }
            
            await self.supabase_client.create_call_metrics(final_data)
            
            logger.info(f"Enhanced analytics finalized for call {self.call_id}: "
                       f"Duration: {self.metrics.duration_seconds:.1f}s, "
                       f"Quality: {self.quality_metrics.overall_score:.2f}, "
                       f"Tokens: {self.metrics.total_tokens}, "
                       f"Interruptions: {self.metrics.interruption_count}")
            
        except Exception as e:
            logger.error(f"Error storing enhanced final call metrics: {e}")
        
        return self.metrics
    
    def _get_sentiment_distribution(self) -> Dict[str, float]:
        """Get sentiment distribution across the call"""
        if not self.sentiment_timeline.sentiments:
            return {"neutral": 1.0}
            
        sentiment_counts = defaultdict(int)
        for sentiment in self.sentiment_timeline.sentiments:
            sentiment_counts[sentiment] += 1
            
        total = len(self.sentiment_timeline.sentiments)
        return {sentiment: count/total for sentiment, count in sentiment_counts.items()}
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive current call metrics"""
        current_duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        return {
            "call_id": self.call_id,
            "duration_seconds": current_duration,
            "total_tokens": self.metrics.total_tokens,
            "interruption_count": self.metrics.interruption_count,
            "sentiment_shifts": self.metrics.sentiment_shifts,
            "conversation_turns": self.conversation_turns,
            "events_captured": len(self.events),
            "final_outcome": self.metrics.final_outcome,
            "quality_metrics": {
                "overall_score": self.quality_metrics.overall_score,
                "clarity_score": self.quality_metrics.clarity_score,
                "engagement_score": self.quality_metrics.engagement_score,
                "efficiency_score": self.quality_metrics.efficiency_score,
                "professional_score": self.quality_metrics.professional_score,
                "completion_score": self.quality_metrics.completion_score
            },
            "voice_metrics": {
                "audio_quality_score": self.voice_metrics.audio_quality_score,
                "interruption_pattern_score": self.voice_metrics.interruption_pattern_score
            },
            "predictions": {
                "expected_duration": self.predictions.expected_duration,
                "likely_outcome": self.predictions.likely_outcome,
                "emergency_probability": self.predictions.emergency_probability,
                "completion_probability": self.predictions.completion_probability,
                "driver_mood_prediction": self.predictions.driver_mood_prediction
            },
            "conversation_analysis": {
                "current_phase": self.current_phase,
                "keyword_frequencies": dict(self.keyword_frequencies),
                "sentiment_timeline": {
                    "current_sentiment": self.last_sentiment,
                    "sentiment_distribution": self._get_sentiment_distribution()
                }
            }
        }


RTVIAnalyticsObserver = EnhancedRTVIAnalyticsObserver