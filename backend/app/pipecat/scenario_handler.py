"""
Scenario Handler for PIPECAT Voice Agent
Implements specific conversation scenarios and response strategies
"""

import logging
from typing import Dict, Any, Optional
from .models import CallContext, ConversationState, ScenarioType, ConversationPhase

logger = logging.getLogger(__name__)


class ScenarioHandler:
    """
    Handles different conversation scenarios with appropriate response strategies
    """
    
    def __init__(self, call_context: CallContext):
        self.call_context = call_context
        self.scenario_type = call_context.scenario_type
    
    def generate_response_prompt(self, 
                               conversation_state: ConversationState,
                               structured_data: Dict[str, Any],
                               user_utterance: str,
                               full_transcript: str) -> str:
        """Generate the appropriate response prompt based on scenario and state"""
        
        # Handle emergency situations first (highest priority)
        if conversation_state.emergency_detected:
            return self._generate_emergency_response_prompt(
                conversation_state, structured_data, user_utterance
            )
        
        # Handle specific scenarios
        if self.scenario_type == ScenarioType.DRIVER_CHECKIN:
            return self._generate_driver_checkin_prompt(
                conversation_state, structured_data, user_utterance, full_transcript
            )
        elif self.scenario_type == ScenarioType.EMERGENCY_PROTOCOL:
            return self._generate_emergency_protocol_prompt(
                conversation_state, structured_data, user_utterance, full_transcript
            )
        else:
            return self._generate_general_logistics_prompt(
                conversation_state, structured_data, user_utterance, full_transcript
            )
    
    def _generate_emergency_response_prompt(self, 
                                          conversation_state: ConversationState,
                                          structured_data: Dict[str, Any],
                                          user_utterance: str) -> str:
        """Generate emergency response prompts"""
        
        base_prompt = f"""
You are an emergency logistics dispatcher handling a critical situation. 
Driver: {self.call_context.driver_name}
Load: {self.call_context.load_number}

EMERGENCY PROTOCOL ACTIVE. Your priorities are:
1. Ensure safety of driver and others
2. Get exact location
3. Understand what happened
4. Escalate to human dispatcher

Current emergency phase: {conversation_state.phase}
"""
        
        safety_status = structured_data.get("safety_status")
        emergency_location = structured_data.get("emergency_location")
        emergency_type = structured_data.get("emergency_type")
        
        if not safety_status:
            return base_prompt + """
IMMEDIATE ACTION REQUIRED: Ask about safety first.
Response: "I understand there may be an emergency situation. First and most importantly - is everyone safe? Are there any injuries that need immediate medical attention?"
"""
        
        elif safety_status and not emergency_location:
            return base_prompt + f"""
Safety confirmed: {safety_status}
NEXT ACTION: Get exact location.
Response: "Thank you for confirming safety. Now I need your exact location. Please give me the highway, mile marker, or nearest exit where you are."
"""
        
        elif emergency_location and not emergency_type:
            return base_prompt + f"""
Safety: {safety_status}
Location: {emergency_location}
NEXT ACTION: Understand what happened.
Response: "Got your location. What exactly happened? Was it an accident, breakdown, or medical emergency?"
"""
        
        else:
            escalation_msg = "I have all the emergency details. I'm connecting you to a human dispatcher right now. Stay on the line and they'll be with you immediately."
            if self.scenario_type == ScenarioType.EMERGENCY_PROTOCOL:
                escalation_msg = "Emergency protocol activated. I have your safety confirmation, location, and incident details. Connecting you to emergency dispatch immediately."
            
            return base_prompt + f"""
All emergency info collected:
Safety: {safety_status}
Location: {emergency_location}
Type: {emergency_type}
FINAL ACTION: Escalate to human dispatcher.
Response: "{escalation_msg}"
END_CALL: true
"""
    
    def _generate_driver_checkin_prompt(self, 
                                      conversation_state: ConversationState,
                                      structured_data: Dict[str, Any],
                                      user_utterance: str,
                                      full_transcript: str) -> str:
        """Generate driver check-in scenario prompts"""
        
        base_prompt = f"""
You are a professional logistics dispatcher conducting a routine driver check-in call.
Driver: {self.call_context.driver_name}
Load: {self.call_context.load_number}

Your goal is to get a comprehensive status update in a friendly, efficient manner.
Current conversation phase: {conversation_state.phase}
Clarification attempts: {conversation_state.clarification_attempts}

User just said: "{user_utterance}"
"""
        
        return base_prompt + self._get_phase_specific_instructions(
            conversation_state, structured_data, "driver_checkin"
        )
    
    def _generate_emergency_protocol_prompt(self, 
                                          conversation_state: ConversationState,
                                          structured_data: Dict[str, Any],
                                          user_utterance: str,
                                          full_transcript: str) -> str:
        """Generate emergency protocol scenario prompts"""
        
        base_prompt = f"""
You are an emergency logistics dispatcher conducting a priority safety check.
Driver: {self.call_context.driver_name}
Load: {self.call_context.load_number}

This is a HIGH PRIORITY call to verify driver safety and status.
Your tone should be professional but urgent. Lead with safety questions.
Current conversation phase: {conversation_state.phase}

User just said: "{user_utterance}"
"""
        
        # Check if emergency keywords detected
        emergency_detected = self._detect_emergency_in_utterance(user_utterance, full_transcript)
        if emergency_detected:
            return base_prompt + """
EMERGENCY KEYWORDS DETECTED in conversation.
IMMEDIATE ACTION: Switch to emergency protocol.
Response: "Emergency detected. Is everyone safe? Any injuries that need immediate medical attention?"
"""
        
        return base_prompt + self._get_phase_specific_instructions(
            conversation_state, structured_data, "emergency_protocol"
        )
    
    def _generate_general_logistics_prompt(self, 
                                         conversation_state: ConversationState,
                                         structured_data: Dict[str, Any],
                                         user_utterance: str,
                                         full_transcript: str) -> str:
        """Generate general logistics scenario prompts"""
        
        base_prompt = f"""
You are a professional logistics dispatcher calling for a routine status update.
Driver: {self.call_context.driver_name}
Load: {self.call_context.load_number}

Maintain a friendly but professional tone. Be efficient but thorough.
Current conversation phase: {conversation_state.phase}
Clarification attempts: {conversation_state.clarification_attempts}

User just said: "{user_utterance}"
"""
        
        return base_prompt + self._get_phase_specific_instructions(
            conversation_state, structured_data, "general"
        )
    
    def _get_phase_specific_instructions(self, 
                                       conversation_state: ConversationState,
                                       structured_data: Dict[str, Any],
                                       scenario_variant: str) -> str:
        """Get instructions specific to the current conversation phase"""
        
        phase = conversation_state.phase
        utterance_lower = conversation_state.get("last_utterance", "").lower()
        
        if phase == ConversationPhase.GREETING:
            if scenario_variant == "emergency_protocol":
                return """
GREETING - Emergency Protocol:
This is the opening of a priority safety check call.
Response: "Hi [Driver Name], this is Emergency Dispatch calling about load [Load Number]. I need to check on your status immediately. Are you safe and do you need any emergency assistance?"
"""
            else:
                return """
GREETING - Standard:
This is the opening of a routine check-in call.
Response: "Hi [Driver Name]! This is Dispatch with a check call on load [Load Number]. Can you give me an update on your status?"
"""
        
        elif phase == ConversationPhase.STATUS_INQUIRY:
            return self._get_status_inquiry_instructions(structured_data, scenario_variant)
        
        elif phase == ConversationPhase.LOCATION_ETA:
            return self._get_location_eta_instructions(structured_data, scenario_variant)
        
        elif phase == ConversationPhase.ARRIVAL_DETAILS:
            return self._get_arrival_details_instructions(structured_data, scenario_variant)
        
        elif phase == ConversationPhase.DELAY_DETAILS:
            return self._get_delay_details_instructions(structured_data, scenario_variant)
        
        elif phase == ConversationPhase.CLARIFICATION:
            return self._get_clarification_instructions(conversation_state, scenario_variant)
        
        elif phase == ConversationPhase.WRAP_UP:
            return self._get_wrap_up_instructions(structured_data, scenario_variant)
        
        else:
            return """
DEFAULT RESPONSE:
Ask for clarification about current status.
Response: "Could you please give me a quick status update on your current situation?"
"""
    
    def _get_status_inquiry_instructions(self, structured_data: Dict[str, Any], scenario_variant: str) -> str:
        """Instructions for status inquiry phase"""
        
        driver_status = structured_data.get("driver_status")
        
        if driver_status == "Driving":
            return """
Driver indicated they are driving/en route.
NEXT: Ask for location and ETA.
Response: "Great, thanks for the update. What's your current location and estimated arrival time?"
"""
        elif driver_status == "Arrived":
            return """
Driver indicated they have arrived.
NEXT: Ask about unloading status.
Response: "Perfect! Are you already unloading or still waiting to get into a dock? What door are you in?"
"""
        elif driver_status == "Delayed":
            return """
Driver indicated there's a delay.
NEXT: Ask about delay details.
Response: "I understand there's a delay. What's causing the delay and when do you expect to arrive?"
"""
        else:
            return """
Driver response unclear about status.
NEXT: Ask for clarification.
Response: "Could you give me a bit more detail about your current situation? Are you driving, at your destination, or experiencing any delays?"
"""
    
    def _get_location_eta_instructions(self, structured_data: Dict[str, Any], scenario_variant: str) -> str:
        """Instructions for location/ETA phase"""
        
        delay_reason = structured_data.get("delay_reason", "None")
        
        if delay_reason != "None":
            return """
Driver provided location/ETA but there may be delays.
NEXT: Check on load and equipment.
Response: "Thanks for the location and ETA. I see there might be some delays. Any issues with your load or equipment I should know about?"
"""
        else:
            return """
Driver provided location/ETA without delays.
NEXT: Check on general concerns.
Response: "Perfect, thanks for the update. Any concerns with your load or truck I should know about?"
"""
    
    def _get_arrival_details_instructions(self, structured_data: Dict[str, Any], scenario_variant: str) -> str:
        """Instructions for arrival details phase"""
        
        unloading_status = structured_data.get("unloading_status", "N/A")
        
        if "Door" in unloading_status:
            return """
Driver is unloading or in a dock door.
NEXT: Check on unloading process.
Response: "Excellent. How's the unloading process going? Any issues with the receiver?"
"""
        else:
            return """
Driver has arrived but status unclear.
NEXT: Clarify unloading status.
Response: "Good to hear you've arrived. Are you unloading or waiting for a dock assignment?"
"""
    
    def _get_delay_details_instructions(self, structured_data: Dict[str, Any], scenario_variant: str) -> str:
        """Instructions for delay details phase"""
        
        return """
Driver provided delay information.
NEXT: Check on load concerns and wrap up.
Response: "I understand about the delay. Keep us updated if anything changes. Any other concerns about your load?"
"""
    
    def _get_clarification_instructions(self, conversation_state: ConversationState, scenario_variant: str) -> str:
        """Instructions for clarification phase"""
        
        attempts = conversation_state.clarification_attempts
        
        if attempts >= 2:
            return """
Too many clarification attempts.
NEXT: Politely end call.
Response: "I'll make a note about your status. Please contact dispatch if you need assistance. Drive safely!"
END_CALL: true
"""
        else:
            return """
Need clarification from driver.
NEXT: Ask for more details.
Response: "I want to make sure I have all the details. Can you tell me more about your current situation?"
"""
    
    def _get_wrap_up_instructions(self, structured_data: Dict[str, Any], scenario_variant: str) -> str:
        """Instructions for wrap-up phase"""
        
        if scenario_variant == "emergency_protocol":
            return """
Emergency protocol check complete - no issues found.
FINAL: Safety reminder and close.
Response: "Emergency protocol complete - no immediate concerns. Drive safely and contact emergency dispatch immediately if any situation changes. Stay vigilant!"
END_CALL: true
"""
        elif scenario_variant == "driver_checkin":
            return """
Driver check-in complete.
FINAL: Professional closing with POD reminder.
Response: "Thank you for the detailed update. Drive safely and remember to submit your POD when you complete the load. Contact us if anything changes!"
END_CALL: true
"""
        else:
            return """
General call wrap-up.
FINAL: Standard professional closing.
Response: "Thank you for the comprehensive update. Drive safely and remember to submit your proof of delivery when you complete the load. Contact us if anything changes!"
END_CALL: true
"""
    
    def _detect_emergency_in_utterance(self, utterance: str, transcript: str) -> bool:
        """Detect emergency keywords in current conversation"""
        emergency_phrases = [
            "emergency", "emergencies", "accident", "breakdown", "medical", 
            "help", "urgent", "blowout", "crash", "collision", "injury", 
            "hurt", "stuck", "disabled", "broke down", "can't move", 
            "need help", "pulled over", "on fire"
        ]
        
        text_to_check = f"{utterance} {transcript}".lower()
        return any(phrase in text_to_check for phrase in emergency_phrases)
    
    def handle_difficult_drivers(self, user_utterance: str, conversation_state: ConversationState) -> str:
        """Handle uncooperative, noisy, or conflicting drivers"""
        
        utterance_lower = user_utterance.lower()
        
        # Uncooperative driver
        if any(phrase in utterance_lower for phrase in ["don't have time", "busy", "can't talk", "leave me alone"]):
            return """
UNCOOPERATIVE DRIVER DETECTED.
Strategy: Be firm but professional, emphasize importance.
Response: "I understand you're busy, but this is a required status check from dispatch. I just need 30 seconds to confirm your location and ETA. This helps us serve our customers better."
"""
        
        # Noisy environment
        if any(phrase in utterance_lower for phrase in ["can't hear", "too loud", "what", "speak up", "noisy"]):
            return """
NOISY ENVIRONMENT DETECTED.
Strategy: Speak clearly, ask them to move somewhere quieter.
Response: "I can hear there's background noise. If possible, could you move somewhere quieter for just a moment? I need to get a quick status update from you."
"""
        
        # Conflicting information
        if conversation_state.clarification_attempts > 0:
            return """
CONFLICTING INFORMATION PATTERN.
Strategy: Be patient, ask specific questions.
Response: "I want to make sure I understand correctly. Let me ask specifically - are you currently driving on the road, or have you arrived at your destination?"
"""
        
        return ""  # No special handling needed