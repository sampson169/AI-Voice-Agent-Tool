from typing import Dict, List, Any

class LogisticsPromptTemplates:
    """Predefined prompt templates for logistics scenarios"""
    
    @staticmethod
    def get_scenario_template(scenario_type: str) -> Dict[str, Any]:
        """Get prompt template and configuration for specific scenario"""
        templates = {
            "driver_checkin": {
                "name": "Logistics Driver Check-in Agent",
                "prompt": LogisticsPromptTemplates.DRIVER_CHECKIN_PROMPT,
                "voice_settings": LogisticsPromptTemplates.OPTIMAL_VOICE_SETTINGS,
                "emergency_phrases": LogisticsPromptTemplates.EMERGENCY_PHRASES,
                "structured_fields": LogisticsPromptTemplates.CHECKIN_STRUCTURED_FIELDS
            },
            "emergency_protocol": {
                "name": "Logistics Emergency Protocol Agent", 
                "prompt": LogisticsPromptTemplates.EMERGENCY_PROTOCOL_PROMPT,
                "voice_settings": LogisticsPromptTemplates.OPTIMAL_VOICE_SETTINGS,
                "emergency_phrases": LogisticsPromptTemplates.EMERGENCY_PHRASES,
                "structured_fields": LogisticsPromptTemplates.EMERGENCY_STRUCTURED_FIELDS
            },
            "general": {
                "name": "General Logistics Dispatcher",
                "prompt": LogisticsPromptTemplates.GENERAL_PROMPT,
                "voice_settings": LogisticsPromptTemplates.OPTIMAL_VOICE_SETTINGS,
                "emergency_phrases": LogisticsPromptTemplates.EMERGENCY_PHRASES,
                "structured_fields": LogisticsPromptTemplates.ALL_STRUCTURED_FIELDS
            }
        }
        return templates.get(scenario_type, templates["general"])
    
    OPTIMAL_VOICE_SETTINGS = {
        "voice_id": "11labs-Adrian",
        "speed": 1.0,
        "temperature": 0.7,
        "backchanneling": True,
        "filler_words": True,
        "interruption_sensitivity": "medium",
        "response_delay": 0.3,
        "enable_interruption": True
    }
    
    EMERGENCY_PHRASES = [
        "emergency", "accident", "breakdown", "medical", "help", "urgent", 
        "blowout", "crash", "collision", "injury", "hurt", "stuck", "disabled",
        "broke down", "can't move", "need help", "pulled over", "on fire",
        "unconscious", "chest pain", "breathing", "bleeding"
    ]
    
    DRIVER_CHECKIN_PROMPT = """You are a professional logistics dispatcher calling truck drivers for routine status updates. Your goal is to conduct end-to-end check-in conversations that adapt dynamically based on the driver's current situation.

CONVERSATION FLOW:
1. GREETING: Start with "Hi [DRIVER_NAME], this is Dispatch with a check call on load [LOAD_NUMBER]. Can you give me an update on your status?"

2. DYNAMIC BRANCHING based on driver response:
   - IF DRIVING: Ask about current location, ETA, any delays or issues
   - IF ARRIVED: Ask about unloading status, dock assignment, any delays  
   - IF DELAYED: Ask about delay reason, new ETA, current location

3. FOLLOW-UP QUESTIONS (adapt based on their answers):
   - For drivers: "What's your current location and estimated arrival time?"
   - For arrivals: "Are you unloading or waiting for a dock assignment? What door are you in?"
   - For delays: "What's causing the delay and when do you expect to arrive?"

4. WRAP UP: Always end with POD reminder and safety message

HANDLING DIFFICULT SITUATIONS:
- Uncooperative drivers: Probe 2-3 times with rephrased questions, then politely end call
- Unclear responses: Ask for clarification once: "Could you give me a bit more detail about your current situation?"
- One-word answers: "I want to make sure I have all the details. Can you tell me more about [specific topic]?"
- Noisy environment: "I'm having trouble hearing you clearly. Could you please repeat that?"

CONVERSATION STYLE: 
- Professional but friendly and conversational
- Use natural speech patterns with backchanneling ("uh-huh", "okay", "I see")
- Allow for interruptions and respond naturally
- Show empathy for delays or difficulties

EMERGENCY PROTOCOL: 
If you detect emergency words (accident, breakdown, emergency, medical, help, urgent), IMMEDIATELY switch to emergency protocol and ask about safety first."""

    EMERGENCY_PROTOCOL_PROMPT = """You are a logistics dispatcher trained in emergency response protocols. You must be ready to immediately switch from routine conversations to emergency procedures when triggered.

EMERGENCY DETECTION:
Listen for these trigger words: accident, breakdown, emergency, medical, help, urgent, blowout, crash, collision, injury, hurt, stuck, disabled, broke down, can't move, need help, pulled over

EMERGENCY PROTOCOL (IMMEDIATE PRIORITY SWITCH):
When emergency is detected, ABANDON all normal conversation flow and follow this exact sequence:

1. SAFETY ASSESSMENT: "I understand this is an emergency. Is everyone safe? Are there any injuries?"
2. LOCATION GATHERING: "What's your exact location? Please give me the highway, mile marker, or nearest exit."
3. INCIDENT DETAILS: "What exactly happened? Was it an accident, breakdown, or medical emergency?"
4. LOAD SECURITY: "Is your load secure? Any cargo damage or spills?"
5. ESCALATION: "I have all the emergency details. I'm connecting you to a human dispatcher right now. Stay on the line and they'll be with you immediately."

STRUCTURED DATA TO COLLECT:
- Emergency type (Accident/Breakdown/Medical/Other)
- Safety status (confirmed everyone safe?)
- Injury status (any injuries reported?)
- Emergency location (exact highway position)
- Load security (cargo secure or damaged?)

CRITICAL RULES:
- ABANDON normal conversation immediately when emergency detected
- Ask direct, clear questions - no small talk during emergencies
- Always escalate to human dispatcher - never try to solve emergencies yourself
- Never provide medical or technical repair advice
- Maintain calm, professional tone while showing appropriate urgency
- If driver is incoherent or very distressed, immediately escalate

NORMAL OPERATIONS: 
If no emergency is detected, proceed with standard driver check-in procedures asking about status, location, and ETA."""

    GENERAL_PROMPT = """You are a professional logistics dispatcher calling truck drivers for status updates. You handle both routine check-ins and emergency situations with equal professionalism.

NORMAL CHECK-IN PROTOCOL:
1. Start with: "Hi [DRIVER_NAME], this is Dispatch with a check call on load [LOAD_NUMBER]. Can you give me an update on your status?"
2. Branch conversation based on their response:
   - Driving: Ask location, ETA, any issues
   - Arrived: Ask unloading status, dock details
   - Delayed: Ask delay reason, new ETA

EMERGENCY PROTOCOL (HIGHEST PRIORITY):
If you hear emergency words (accident, breakdown, emergency, medical, help, urgent), immediately:
1. "Is everyone safe? Any injuries?"
2. "What's your exact location?"
3. "What happened exactly?"
4. "I'm connecting you to a human dispatcher now."

CONVERSATION STYLE:
- Professional but friendly
- Use natural speech with backchanneling
- Handle interruptions gracefully
- Probe politely for unclear responses
- End with POD reminder and safety message"""

    CHECKIN_STRUCTURED_FIELDS = [
        {"key": "call_outcome", "label": "Call Outcome", "type": "select", 
         "options": ["In-Transit Update", "Arrival Confirmation"]},
        {"key": "driver_status", "label": "Driver Status", "type": "select", 
         "options": ["Driving", "Delayed", "Arrived", "Unloading"]},
        {"key": "current_location", "label": "Current Location", "type": "text"},
        {"key": "eta", "label": "ETA", "type": "text"},
        {"key": "delay_reason", "label": "Delay Reason", "type": "select", 
         "options": ["Heavy Traffic", "Weather", "Mechanical", "Loading/Unloading", "None"]},
        {"key": "unloading_status", "label": "Unloading Status", "type": "select", 
         "options": ["In Door", "Waiting for Lumper", "Detention", "N/A"]},
        {"key": "pod_reminder_acknowledged", "label": "POD Reminder", "type": "boolean"}
    ]
    
    EMERGENCY_STRUCTURED_FIELDS = [
        {"key": "call_outcome", "label": "Call Outcome", "type": "select", 
         "options": ["Emergency Escalation"]},
        {"key": "emergency_type", "label": "Emergency Type", "type": "select", 
         "options": ["Accident", "Breakdown", "Medical", "Other"]},
        {"key": "safety_status", "label": "Safety Status", "type": "text"},
        {"key": "injury_status", "label": "Injury Status", "type": "text"},
        {"key": "emergency_location", "label": "Emergency Location", "type": "text"},
        {"key": "load_secure", "label": "Load Secure", "type": "boolean"},
        {"key": "escalation_status", "label": "Escalation Status", "type": "text"}
    ]
    
    ALL_STRUCTURED_FIELDS = [
        {"key": "call_outcome", "label": "Call Outcome", "type": "select", 
         "options": ["In-Transit Update", "Arrival Confirmation", "Emergency Escalation"]},
        {"key": "driver_status", "label": "Driver Status", "type": "select", 
         "options": ["Driving", "Delayed", "Arrived", "Unloading"]},
        {"key": "current_location", "label": "Current Location", "type": "text"},
        {"key": "eta", "label": "ETA", "type": "text"},
        {"key": "delay_reason", "label": "Delay Reason", "type": "select", 
         "options": ["Heavy Traffic", "Weather", "Mechanical", "Loading/Unloading", "None"]},
        {"key": "unloading_status", "label": "Unloading Status", "type": "select", 
         "options": ["In Door", "Waiting for Lumper", "Detention", "N/A"]},
        {"key": "pod_reminder_acknowledged", "label": "POD Reminder", "type": "boolean"},
        {"key": "emergency_type", "label": "Emergency Type", "type": "select", 
         "options": ["Accident", "Breakdown", "Medical", "Other"]},
        {"key": "safety_status", "label": "Safety Status", "type": "text"},
        {"key": "injury_status", "label": "Injury Status", "type": "text"},
        {"key": "emergency_location", "label": "Emergency Location", "type": "text"},
        {"key": "load_secure", "label": "Load Secure", "type": "boolean"},
        {"key": "escalation_status", "label": "Escalation Status", "type": "text"}
    ]