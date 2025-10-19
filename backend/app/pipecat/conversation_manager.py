"""
Conversation Manager for PIPECAT Voice Agent
Handles conversation flow, emergency detection, and structured data extraction
"""

import logging
import re
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from .models import (
    CallContext, ConversationState, StructuredData, ConversationPhase,
    CallOutcome, DriverStatus, EmergencyType, ScenarioType
)
from .scenario_handler import ScenarioHandler

logger = logging.getLogger(__name__)


class ConversationManager:
    """
    Manages conversation flow and extracts structured data from interactions
    Replaces the webhook logic with PIPECAT-native processing
    """
    
    def __init__(self, call_context: CallContext, supabase_client):
        self.call_context = call_context
        self.supabase_client = supabase_client
        self.conversation_state = ConversationState(
            scenario_type=call_context.scenario_type
        )
        self.structured_data = StructuredData()
        self.full_transcript = ""
        self.analytics_observer = None
        self.scenario_handler = ScenarioHandler(call_context)
        
        logger.info(f"ConversationManager initialized for call {call_context.call_id}, "
                   f"scenario: {call_context.scenario_type}")
    
    def set_analytics_observer(self, observer):
        """Set the analytics observer for this conversation"""
        self.analytics_observer = observer
    
    async def process_frame(self, frame) -> None:
        """Process incoming PIPECAT frames"""
        try:
            frame_type = type(frame).__name__
            
            if frame_type == "TranscriptionFrame":
                await self._process_transcription(frame)
            elif frame_type == "LLMMessagesFrame":
                await self._process_llm_messages(frame)
                
        except Exception as e:
            logger.error(f"Error processing frame in conversation manager: {e}")
    
    async def _process_transcription(self, frame) -> None:
        """Process user transcription and update conversation state"""
        if not hasattr(frame, 'text'):
            return
            
        user_utterance = frame.text
        self.full_transcript += f"User: {user_utterance}\n"
        
        # Check for emergency
        emergency_detected = self._detect_emergency(user_utterance, self.full_transcript)
        
        if emergency_detected and not self.conversation_state.emergency_detected:
            logger.warning(f"🚨 Emergency detected in call {self.call_context.call_id}")
            self.conversation_state.emergency_detected = True
            self.conversation_state.phase = ConversationPhase.EMERGENCY
        
        # Update conversation state based on current utterance
        if not self.conversation_state.emergency_detected:
            self._update_conversation_phase(user_utterance)
        
        # Extract structured data
        self._extract_structured_data()
        
        # Update analytics observer
        if self.analytics_observer:
            await self.analytics_observer.update_conversation_state(self.conversation_state)
        
        # Store updated data in database
        await self._store_conversation_data()
        
        logger.debug(f"Processed transcription for {self.call_context.call_id}: "
                    f"Phase={self.conversation_state.phase}, "
                    f"Emergency={self.conversation_state.emergency_detected}")
    
    async def _process_llm_messages(self, frame) -> None:
        """Process LLM response messages"""
        try:
            if hasattr(frame, 'messages') and frame.messages:
                for message in frame.messages:
                    if message.get('role') == 'assistant':
                        content = message.get('content', '')
                        self.full_transcript += f"Agent: {content}\n"
                        
                        # Check if this response indicates call ending
                        if self._is_call_ending_response(content):
                            await self._finalize_call()
                            
        except Exception as e:
            logger.error(f"Error processing LLM messages: {e}")
    
    def _detect_emergency(self, current_utterance: str, transcript: str) -> bool:
        """Detect emergency situations in conversation"""
        emergency_phrases = [
            "emergency", "emergencies", "accident", "breakdown", "medical", 
            "help", "urgent", "blowout", "crash", "collision", "injury", 
            "hurt", "stuck", "disabled", "broke down", "can't move", 
            "need help", "pulled over", "on fire", "unconscious", 
            "chest pain", "breathing", "bleeding", "trouble", "problem"
        ]
        
        text_to_check = f"{current_utterance} {transcript}".lower()
        
        for phrase in emergency_phrases:
            if phrase in text_to_check:
                logger.info(f"Emergency detected: Found '{phrase}' in conversation")
                return True
        
        return False
    
    def _update_conversation_phase(self, utterance: str) -> None:
        """Update conversation phase based on user input"""
        utterance_lower = utterance.lower()
        current_phase = self.conversation_state.phase
        
        if current_phase == ConversationPhase.GREETING:
            self.conversation_state.phase = ConversationPhase.STATUS_INQUIRY
        
        elif current_phase == ConversationPhase.STATUS_INQUIRY:
            if any(word in utterance_lower for word in ["driving", "on the road", "en route"]):
                self.conversation_state.phase = ConversationPhase.LOCATION_ETA
            elif any(word in utterance_lower for word in ["arrived", "here", "at dock", "unloading"]):
                self.conversation_state.phase = ConversationPhase.ARRIVAL_DETAILS
            elif any(word in utterance_lower for word in ["delayed", "late", "behind", "stuck"]):
                self.conversation_state.phase = ConversationPhase.DELAY_DETAILS
            else:
                self.conversation_state.phase = ConversationPhase.CLARIFICATION
        
        elif current_phase == ConversationPhase.LOCATION_ETA:
            if "delay" in self.structured_data.delay_reason.lower() if self.structured_data.delay_reason else False:
                self.conversation_state.phase = ConversationPhase.DELAY_DETAILS
            else:
                self.conversation_state.phase = ConversationPhase.WRAP_UP
        
        elif current_phase == ConversationPhase.ARRIVAL_DETAILS:
            self.conversation_state.phase = ConversationPhase.WRAP_UP
        
        elif current_phase == ConversationPhase.DELAY_DETAILS:
            self.conversation_state.phase = ConversationPhase.WRAP_UP
        
        elif current_phase == ConversationPhase.CLARIFICATION:
            self.conversation_state.clarification_attempts += 1
            if self.conversation_state.clarification_attempts >= 2:
                self.conversation_state.phase = ConversationPhase.WRAP_UP
            else:
                self.conversation_state.phase = ConversationPhase.STATUS_INQUIRY
    
    def _extract_structured_data(self) -> None:
        """Extract structured data from the conversation transcript"""
        text_lower = self.full_transcript.lower()
        
        # Determine call outcome
        if self.conversation_state.emergency_detected:
            self.structured_data.call_outcome = CallOutcome.EMERGENCY_ESCALATION
            self._extract_emergency_data(text_lower)
        elif any(word in text_lower for word in ["arrived", "here", "at the dock", "destination"]):
            self.structured_data.call_outcome = CallOutcome.ARRIVAL_CONFIRMATION
            self.structured_data.driver_status = DriverStatus.ARRIVED
        else:
            self.structured_data.call_outcome = CallOutcome.IN_TRANSIT_UPDATE
            
            if any(word in text_lower for word in ["delayed", "late", "behind schedule"]):
                self.structured_data.driver_status = DriverStatus.DELAYED
            else:
                self.structured_data.driver_status = DriverStatus.DRIVING
        
        # Extract location
        location = self._extract_location_from_text(text_lower)
        if location:
            if self.conversation_state.emergency_detected:
                self.structured_data.emergency_location = location
            else:
                self.structured_data.current_location = location
        
        # Extract ETA
        eta = self._extract_eta_from_text(text_lower)
        if eta:
            self.structured_data.eta = eta
        
        # Extract delay reason
        self.structured_data.delay_reason = self._extract_delay_reason(text_lower)
        
        # Check for POD reminder acknowledgment
        self.structured_data.pod_reminder_acknowledged = any(
            phrase in text_lower for phrase in [
                "pod", "proof of delivery", "paperwork", "receipt", "delivery confirmation"
            ]
        )
        
        # Extract unloading status
        if "unloading" in text_lower or "door" in text_lower:
            door_match = re.search(r"door\s*(\d+)", text_lower)
            if door_match:
                self.structured_data.unloading_status = f"In Door {door_match.group(1)}"
            elif "waiting" in text_lower:
                self.structured_data.unloading_status = "Waiting for Lumper"
            elif "detention" in text_lower:
                self.structured_data.unloading_status = "Detention"
            else:
                self.structured_data.unloading_status = "In Door"
        else:
            self.structured_data.unloading_status = "N/A"
    
    def _extract_emergency_data(self, text_lower: str) -> None:
        """Extract emergency-specific data"""
        # Determine emergency type
        if any(word in text_lower for word in ["accident", "crash", "collision", "hit"]):
            self.structured_data.emergency_type = EmergencyType.ACCIDENT
        elif any(word in text_lower for word in ["breakdown", "broke down", "mechanical", "engine", "tire"]):
            self.structured_data.emergency_type = EmergencyType.BREAKDOWN
        elif any(word in text_lower for word in ["medical", "injury", "hurt", "sick", "chest pain"]):
            self.structured_data.emergency_type = EmergencyType.MEDICAL
        else:
            self.structured_data.emergency_type = EmergencyType.OTHER
        
        # Extract safety status
        if any(phrase in text_lower for phrase in ["everyone is safe", "we're safe", "no one hurt"]):
            self.structured_data.safety_status = "Driver confirmed everyone is safe"
        elif any(phrase in text_lower for phrase in ["not safe", "unsafe", "danger"]):
            self.structured_data.safety_status = "Safety concerns reported"
        else:
            self.structured_data.safety_status = "Safety status unknown"
        
        # Extract injury status
        if any(word in text_lower for word in ["injury", "hurt", "injured", "bleeding"]):
            self.structured_data.injury_status = "Injuries reported"
        elif any(phrase in text_lower for phrase in ["no injuries", "no one hurt", "not injured"]):
            self.structured_data.injury_status = "No injuries reported"
        else:
            self.structured_data.injury_status = "Injury status unknown"
        
        # Check load security
        if any(phrase in text_lower for phrase in ["load is secure", "cargo secure", "load safe"]):
            self.structured_data.load_secure = True
        elif any(phrase in text_lower for phrase in ["load shifted", "cargo damaged", "spilled"]):
            self.structured_data.load_secure = False
        
        self.structured_data.escalation_status = "Connected to Human Dispatcher"
    
    def _extract_location_from_text(self, text: str) -> str:
        """Extract location information from text"""
        location_patterns = [
            r"(i-\d+[^,\s]*(?:\s+(?:north|south|east|west))?)",
            r"(interstate \d+[^,\s]*)",
            r"(mile marker \d+[^,\s]*)",
            r"(exit \d+[^,\s]*)",
            r"(highway \d+[^,\s]*)",
            r"(route \d+[^,\s]*)",
            r"(us \d+[^,\s]*)",
            r"(?:near|at|in)\s+([a-z]+(?:\s+[a-z]+)*)",
            r"([a-z]+\s+city)",
            r"([a-z]+\s+county)"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        return ""
    
    def _extract_eta_from_text(self, text: str) -> str:
        """Extract ETA information from text"""
        eta_patterns = [
            r"(\d{1,2}:\d{2}\s*(?:am|pm)?)",
            r"(\d{1,2}\s*(?:am|pm))",
            r"(tomorrow(?:\s+(?:morning|afternoon|evening))?)",
            r"(today(?:\s+(?:morning|afternoon|evening))?)",
            r"(\d+\s*hours?)",
            r"(\d+\s*minutes?)",
            r"(in\s+\d+\s*(?:hours?|minutes?))",
            r"(around\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)?)"
        ]
        
        for pattern in eta_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1) if len(match.groups()) > 0 else match.group(0)
        
        return ""
    
    def _extract_delay_reason(self, text: str) -> str:
        """Extract delay reason from text"""
        if any(word in text for word in ["traffic", "congestion", "jam"]):
            return "Heavy Traffic"
        elif any(word in text for word in ["weather", "rain", "snow", "storm", "fog"]):
            return "Weather"
        elif any(word in text for word in ["mechanical", "breakdown", "engine", "tire", "maintenance"]):
            return "Mechanical"
        elif any(word in text for word in ["loading", "unloading", "shipper", "receiver", "warehouse"]):
            return "Loading/Unloading"
        elif any(word in text for word in ["delayed", "late", "behind"]):
            return "Other"
        else:
            return "None"
    
    def _is_call_ending_response(self, response: str) -> bool:
        """Check if the agent response indicates call is ending"""
        ending_phrases = [
            "drive safely",
            "thank you for",
            "contact us if",
            "connecting you to",
            "human dispatcher",
            "end of call",
            "goodbye",
            "have a good day"
        ]
        
        response_lower = response.lower()
        return any(phrase in response_lower for phrase in ending_phrases)
    
    async def _store_conversation_data(self) -> None:
        """Store current conversation data in Supabase"""
        try:
            call_data = {
                "transcript": self.full_transcript,
                "summary": self.structured_data.dict(),
                "conversation_state": self.conversation_state.dict()
            }
            
            await self.supabase_client.update_call_result(self.call_context.call_id, call_data)
            
        except Exception as e:
            logger.error(f"Error storing conversation data: {e}")
    
    async def _finalize_call(self) -> None:
        """Finalize the call and store final data"""
        try:
            # Final data extraction
            self._extract_structured_data()
            
            # Store final call data
            final_data = {
                "transcript": self.full_transcript,
                "summary": self.structured_data.dict(),
                "conversation_state": self.conversation_state.dict(),
                "duration": (datetime.utcnow() - datetime.fromisoformat(
                    self.call_context.call_id.split('-')[0] if '-' in self.call_context.call_id else 
                    datetime.utcnow().isoformat()
                )).total_seconds() if hasattr(self, 'start_time') else 0
            }
            
            await self.supabase_client.update_call_result(self.call_context.call_id, final_data)
            
            logger.info(f"Finalized call {self.call_context.call_id} with outcome: "
                       f"{self.structured_data.call_outcome}")
            
        except Exception as e:
            logger.error(f"Error finalizing call: {e}")
    
    def generate_next_response_context(self) -> Dict[str, Any]:
        """Generate context for the next LLM response"""
        
        # Get the last user utterance
        transcript_lines = self.full_transcript.strip().split('\n')
        last_user_utterance = ""
        for line in reversed(transcript_lines):
            if line.startswith("User: "):
                last_user_utterance = line[6:]  # Remove "User: " prefix
                break
        
        # Store last utterance for scenario handler
        self.conversation_state.last_utterance = last_user_utterance
        
        # Generate scenario-specific response prompt
        response_prompt = self.scenario_handler.generate_response_prompt(
            conversation_state=self.conversation_state,
            structured_data=self.structured_data.dict(),
            user_utterance=last_user_utterance,
            full_transcript=self.full_transcript
        )
        
        # Check for difficult driver patterns
        difficult_driver_handling = self.scenario_handler.handle_difficult_drivers(
            user_utterance=last_user_utterance,
            conversation_state=self.conversation_state
        )
        
        if difficult_driver_handling:
            response_prompt += f"\n\nSPECIAL HANDLING REQUIRED:\n{difficult_driver_handling}"
        
        return {
            "call_context": self.call_context.dict(),
            "conversation_state": self.conversation_state.dict(),
            "structured_data": self.structured_data.dict(),
            "current_phase": self.conversation_state.phase,
            "emergency_detected": self.conversation_state.emergency_detected,
            "scenario_type": self.call_context.scenario_type,
            "response_prompt": response_prompt,
            "last_user_utterance": last_user_utterance,
            "full_transcript": self.full_transcript
        }