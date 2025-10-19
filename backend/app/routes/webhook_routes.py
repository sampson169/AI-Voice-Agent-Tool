"""
DEPRECATED: Retell AI Webhook Routes
This module is being phased out as part of the PIPECAT migration.
These routes are kept for backwards compatibility during the transition period.
"""

from fastapi import APIRouter, Request, HTTPException, WebSocket, WebSocketDisconnect
from app.database.supabase import supabase_client
from app.models.schemas import RetellWebhook
import json
import re
from typing import Dict, Any
import warnings

# Issue deprecation warning
warnings.warn(
    "webhook_routes.py is deprecated and will be removed in a future version. "
    "Use PIPECAT voice agent instead.",
    DeprecationWarning,
    stacklevel=2
)

router = APIRouter(prefix="/api/webhook", tags=["webhook", "deprecated"])

@router.get("/test")
async def test_webhook():
    return {"status": "ok", "message": "Webhook endpoint is accessible"}

@router.websocket("/retell/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            
            call_id = message.get("call_id")
            if call_id:
                response = await process_websocket_message(message, call_id)
                if response is not None:
                    await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close()

@router.websocket("/retell/ws/{call_id}")
async def websocket_call_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            
            response = await process_websocket_message(message, call_id)
            if response is not None:
                await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close()

@router.websocket("/retell/{call_id}")  
async def websocket_retell_endpoint(websocket: WebSocket, call_id: str):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_json()
            
            response = await process_websocket_message(message, call_id)
            if response is not None:
                await websocket.send_text(json.dumps(response))
            
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close()

@router.post("/retell")
async def handle_retell_webhook(request: Request):
    try:
        webhook_data = await request.json()
        
        response = await process_retell_webhook(webhook_data)
        return response
        
    except Exception as e:
        fallback_response = {
            "response": "I apologize for the technical difficulty. This is Dispatch calling for a status update. Can you please tell me your current location?",
            "response_id": 1,
            "end_call": False
        }
        return fallback_response

async def process_websocket_message(message: dict, call_id: str) -> dict:
    try:
        message_type = message.get("type") or message.get("interaction_type")
        
        if message_type == "response_required":
            transcript_array = message.get("transcript", [])
            
            full_transcript = ""
            last_user_utterance = ""
            
            for item in transcript_array:
                role = item.get("role", "")
                content = item.get("content", "")
                if role == "user":
                    full_transcript += f"User: {content}\n"
                    last_user_utterance = content
                elif role == "agent":
                    full_transcript += f"Agent: {content}\n"
            
            call_data = await supabase_client.get_call_result(call_id)
            if not call_data:
                retell_vars = message.get("retell_llm_dynamic_variables", {})
                driver_name = retell_vars.get("driver_name", "Driver")
                load_number = retell_vars.get("load_number", "Load")
                
                call_data = {
                    "id": call_id,
                    "call_request": {
                        "driverName": driver_name,
                        "loadNumber": load_number,
                        "agentId": "agent_fa51b58953a177984c9e173910"
                    },
                    "conversation_state": {
                        "phase": "greeting",
                        "emergency_detected": False,
                        "clarification_attempts": 0,
                        "scenario_type": "general"
                    },
                    "transcript": full_transcript,
                    "summary": {}
                }
                
                await supabase_client.create_call_result(call_data)
            
            response_data = await process_retell_webhook({
                "call_id": call_id,
                "transcript": full_transcript,
                "last_user_utterance": last_user_utterance
            })
            
            websocket_response = {
                "response_id": message.get("response_id", 1),
                "content": response_data.get("response", ""),
                "content_complete": True,
                "end_call": response_data.get("end_call", False)
            }
            
            return websocket_response
            
        elif message_type == "ping":
            return {"type": "pong"}
            
        elif message_type in ["update_only"]:
            return None
            
        else:
            return None
            
    except Exception as e:
        return {
            "response_id": 1,
            "content": "I apologize for the technical difficulty. This is Dispatch calling for a status update. Can you tell me your current location?",
            "content_complete": True,
            "end_call": False
        }

async def process_retell_webhook(webhook_data: dict) -> dict:
    call_id = webhook_data.get("call_id")
    if not call_id and "call" in webhook_data:
        call_id = webhook_data["call"].get("call_id")
    
    transcript = webhook_data.get("transcript", "")
    current_utterance = webhook_data.get("last_user_utterance", "").lower()
    
    event_type = webhook_data.get("event")
    if event_type:
        
        if event_type == "call_started":
            call_info = webhook_data.get("call", {})
            retell_vars = call_info.get("retell_llm_dynamic_variables", {})
            
            if retell_vars:
                call_data = await supabase_client.get_call_result(call_id)
                if call_data:
                    call_data["call_request"]["driverName"] = retell_vars.get("driver_name", "Driver")
                    call_data["call_request"]["loadNumber"] = retell_vars.get("load_number", "Load")
                    scenario_type = retell_vars.get("scenario_type", "general")
                    if "conversation_state" not in call_data:
                        call_data["conversation_state"] = {}
                    call_data["conversation_state"]["scenario_type"] = scenario_type
                    await supabase_client.update_call_result(call_id, call_data)
                else:
                    scenario_type = retell_vars.get("scenario_type", "general")
                    call_data = {
                        "id": call_id,
                        "call_request": {
                            "driverName": retell_vars.get("driver_name", "Driver"),
                            "loadNumber": retell_vars.get("load_number", "Load"),
                            "agentId": retell_vars.get("agent_id", "agent_fa51b58953a177984c9e173910")
                        },
                        "conversation_state": {
                            "phase": "greeting",
                            "emergency_detected": False,
                            "clarification_attempts": 0,
                            "scenario_type": scenario_type
                        },
                        "transcript": "",
                        "summary": {}
                    }
                    await supabase_client.create_call_result(call_data)
        
        if event_type in ["call_started", "call_ended", "call_analyzed"]:
            return {
                "response": "Event received",
                "response_id": 1,
                "end_call": event_type == "call_ended" or event_type == "call_analyzed"
            }
    
    call_data = await supabase_client.get_call_result(call_id)
    if not call_data:
        call_data = {
            "id": call_id,
            "call_request": {
                "driverName": "Mike",
                "loadNumber": "Jonson",
                "agentId": "test-agent"
            },
            "conversation_state": {
                "phase": "status_inquiry",
                "emergency_detected": False,
                "clarification_attempts": 0,
                "scenario_type": "general"
            },
            "transcript": transcript,
            "summary": {}
        }
        
        await supabase_client.create_call_result(call_data)
        print(f"📝 Created new call data for testing: {call_id}")
    
    call_request = call_data.get("call_request", {})
    conversation_state = call_data.get("conversation_state", {"phase": "greeting", "emergency_detected": False, "scenario_type": "general"})
    
    scenario_type = conversation_state.get("scenario_type", "general")
    
    emergency_detected = detect_emergency(current_utterance, transcript)
    
    summary = extract_structured_data(transcript, call_request, conversation_state)
    
    if emergency_detected and not conversation_state.get("emergency_detected", False):
        print(f"🚨 EMERGENCY ACTIVATED: Setting emergency mode")
        conversation_state["emergency_detected"] = True
        conversation_state["phase"] = "emergency"
    elif not conversation_state.get("emergency_detected", False):
        conversation_state = update_conversation_state(current_utterance, transcript, conversation_state, summary)
    
    print(f"📊 Final Conversation State:")
    print(f"   Phase: {conversation_state.get('phase')}")
    print(f"   Emergency Detected: {conversation_state.get('emergency_detected')}")
    print(f"   Scenario Type: {scenario_type}")
    
    updated_data = {
        "transcript": transcript,
        "summary": summary,
        "conversation_state": conversation_state
    }
    await supabase_client.update_call_result(call_id, updated_data)
    
    return generate_conversation_response(current_utterance, transcript, call_data, summary, conversation_state, scenario_type)

def detect_emergency(current_utterance: str, transcript: str) -> bool:
    emergency_phrases = [
        "emergency", "emergencies", "accident", "breakdown", "medical", "help", "urgent", 
        "blowout", "crash", "collision", "injury", "hurt", "stuck", "disabled",
        "broke down", "can't move", "need help", "pulled over", "on fire",
        "unconscious", "chest pain", "breathing", "bleeding", "trouble", "problem"
    ]
    
    text_to_check = f"{current_utterance} {transcript}".lower()
    
    print(f"🔍 Emergency Detection Debug:")
    print(f"   Current utterance: '{current_utterance}'")
    print(f"   Text to check: '{text_to_check}'")
    
    for phrase in emergency_phrases:
        if phrase in text_to_check:
            print(f"   ⚠️  EMERGENCY DETECTED: Found '{phrase}' in text")
            return True
    
    print(f"   ✅ No emergency keywords found")
    return False

def update_conversation_state(current_utterance: str, transcript: str, 
                            conversation_state: Dict[str, Any], summary: dict) -> Dict[str, Any]:
    current_phase = conversation_state.get("phase", "greeting")
    
    if conversation_state.get("emergency_detected", False):
        conversation_state["phase"] = "emergency"
        return conversation_state
    
    utterance_lower = current_utterance.lower()
    
    if current_phase == "greeting":
        conversation_state["phase"] = "status_inquiry"
    
    elif current_phase == "status_inquiry":
        if any(word in utterance_lower for word in ["driving", "on the road", "en route"]):
            conversation_state["phase"] = "location_eta"
        elif any(word in utterance_lower for word in ["arrived", "here", "at dock", "unloading"]):
            conversation_state["phase"] = "arrival_details"
        elif any(word in utterance_lower for word in ["delayed", "late", "behind", "stuck"]):
            conversation_state["phase"] = "delay_details"
        else:
            conversation_state["phase"] = "clarification"
    
    elif current_phase == "location_eta":
        if "delay" in summary.get("delay_reason", "").lower() or summary.get("delay_reason") != "None":
            conversation_state["phase"] = "delay_details"
        else:
            conversation_state["phase"] = "wrap_up"
    
    elif current_phase == "arrival_details":
        conversation_state["phase"] = "wrap_up"
    
    elif current_phase == "delay_details":
        conversation_state["phase"] = "wrap_up"
    
    elif current_phase == "clarification":
        conversation_state["clarification_attempts"] = conversation_state.get("clarification_attempts", 0) + 1
        if conversation_state["clarification_attempts"] >= 2:
            conversation_state["phase"] = "wrap_up"
        else:
            conversation_state["phase"] = "status_inquiry"
    
    return conversation_state

def extract_structured_data(transcript: str, call_request: dict, conversation_state: Dict[str, Any] = None) -> dict:
    summary = {}
    text_lower = transcript.lower()
    is_emergency = conversation_state and conversation_state.get("emergency_detected", False)
    
    if is_emergency or detect_emergency("", transcript):
        summary["call_outcome"] = "Emergency Escalation"
        
        if any(word in text_lower for word in ["accident", "crash", "collision", "hit"]):
            summary["emergency_type"] = "Accident"
        elif any(word in text_lower for word in ["breakdown", "broke down", "mechanical", "engine", "tire", "blowout"]):
            summary["emergency_type"] = "Breakdown"
        elif any(word in text_lower for word in ["medical", "injury", "hurt", "sick", "chest pain", "dizzy"]):
            summary["emergency_type"] = "Medical"
        else:
            summary["emergency_type"] = "Other"
        
        if any(phrase in text_lower for phrase in ["everyone is safe", "we're safe", "no one hurt", "all safe"]):
            summary["safety_status"] = "Driver confirmed everyone is safe"
        elif any(phrase in text_lower for phrase in ["not safe", "unsafe", "danger"]):
            summary["safety_status"] = "Safety concerns reported"
        else:
            summary["safety_status"] = "Safety status unknown"
        
        if any(word in text_lower for word in ["injury", "hurt", "injured", "bleeding", "unconscious"]):
            summary["injury_status"] = "Injuries reported"
        elif any(phrase in text_lower for phrase in ["no injuries", "no one hurt", "not injured", "fine"]):
            summary["injury_status"] = "No injuries reported"
        else:
            summary["injury_status"] = "Injury status unknown"
        
        emergency_location = extract_location_from_text(text_lower, emergency_context=True)
        if emergency_location:
            summary["emergency_location"] = emergency_location
        
        if any(phrase in text_lower for phrase in ["load is secure", "cargo secure", "load safe"]):
            summary["load_secure"] = True
        elif any(phrase in text_lower for phrase in ["load shifted", "cargo damaged", "spilled"]):
            summary["load_secure"] = False
        else:
            summary["load_secure"] = None
        
        summary["escalation_status"] = "Connected to Human Dispatcher"
        
    else:
        if any(word in text_lower for word in ["arrived", "here", "at the dock", "at destination", "delivery"]):
            summary["call_outcome"] = "Arrival Confirmation"
            summary["driver_status"] = "Arrived"
            
            if any(word in text_lower for word in ["unloading", "dock", "door"]):
                summary["driver_status"] = "Unloading"
                door_match = re.search(r"door\s*(\d+)", text_lower)
                if door_match:
                    summary["unloading_status"] = f"In Door {door_match.group(1)}"
                elif "waiting" in text_lower:
                    summary["unloading_status"] = "Waiting for Lumper"
                elif "detention" in text_lower:
                    summary["unloading_status"] = "Detention"
                else:
                    summary["unloading_status"] = "In Door"
            else:
                summary["unloading_status"] = "N/A"
        else:
            summary["call_outcome"] = "In-Transit Update"
            
            if any(word in text_lower for word in ["delayed", "late", "behind schedule", "running late"]):
                summary["driver_status"] = "Delayed"
            else:
                summary["driver_status"] = "Driving"
            
            summary["unloading_status"] = "N/A"
    
    if not is_emergency:
        location = extract_location_from_text(text_lower)
        if location:
            summary["current_location"] = location
    
    eta = extract_eta_from_text(text_lower)
    if eta:
        summary["eta"] = eta
    
    delay_reason = extract_delay_reason(text_lower)
    summary["delay_reason"] = delay_reason
    
    summary["pod_reminder_acknowledged"] = any(phrase in text_lower for phrase in [
        "pod", "proof of delivery", "paperwork", "receipt", "delivery confirmation"
    ])
    
    return summary

def extract_location_from_text(text: str, emergency_context: bool = False) -> str:
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

def extract_eta_from_text(text: str) -> str:
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

def extract_delay_reason(text: str) -> str:
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

def generate_conversation_response(utterance: str, transcript: str, call_data: dict, 
                                 summary: dict, conversation_state: Dict[str, Any], scenario_type: str = "general") -> dict:
    call_request = call_data.get("call_request", {})
    driver_name = call_request.get("driverName", "")
    load_number = call_request.get("loadNumber", "")
    current_phase = conversation_state.get("phase", "greeting")
    
    if conversation_state.get("emergency_detected", False):
        return handle_emergency_response(summary, current_phase, scenario_type)
    
    if scenario_type == "driver_checkin":
        return generate_driver_checkin_response(utterance, transcript, call_request, summary, conversation_state)
    elif scenario_type == "emergency_protocol":
        return generate_emergency_protocol_response(utterance, transcript, call_request, summary, conversation_state)
    else:
        return generate_general_response(utterance, transcript, call_request, summary, conversation_state)

def handle_emergency_response(summary: dict, current_phase: str, scenario_type: str) -> dict:
    
    print(f"🚨 Emergency Response Handler:")
    print(f"   Phase: {current_phase}")
    print(f"   Summary: {summary}")
    print(f"   Scenario Type: {scenario_type}")
    
    if current_phase == "emergency" and not summary.get("safety_status"):
        return {
            "response": "I understand there may be an emergency situation. First and most importantly - is everyone safe? Are there any injuries that need immediate medical attention?",
            "response_id": 1,
            "end_call": False
        }
    elif summary.get("safety_status") and not summary.get("emergency_location"):
        return {
            "response": "Thank you for confirming safety. Now I need your exact location. Please give me the highway, mile marker, or nearest exit where you are.",
            "response_id": 1,
            "end_call": False
        }
    elif summary.get("emergency_location") and not summary.get("emergency_type"):
        return {
            "response": "Got your location. What exactly happened? Was it an accident, breakdown, or medical emergency?",
            "response_id": 1,
            "end_call": False
        }
    else:
        escalation_msg = "I have all the emergency details. I'm connecting you to a human dispatcher right now. Stay on the line and they'll be with you immediately."
        if scenario_type == "emergency_protocol":
            escalation_msg = "Emergency protocol activated. I have your safety confirmation, location, and incident details. Connecting you to emergency dispatch immediately."
        return {
            "response": escalation_msg,
            "response_id": 1,
            "end_call": True
        }

def generate_driver_checkin_response(utterance: str, transcript: str, call_request: dict, 
                                   summary: dict, conversation_state: Dict[str, Any]) -> dict:
    driver_name = call_request.get("driverName", "")
    load_number = call_request.get("loadNumber", "")
    current_phase = conversation_state.get("phase", "greeting")
    utterance_lower = utterance.lower()
    
    if current_phase == "greeting" or not transcript or len(transcript.split()) < 10:
        return {
            "response": f"Hi {driver_name}! This is Dispatch with a check call on load {load_number}. Can you give me an update on your status?",
            "response_id": 1,
            "end_call": False
        }
    
    elif current_phase == "status_inquiry":
        if any(word in utterance_lower for word in ["driving", "on the road", "en route", "heading"]):
            return {
                "response": "Great, thanks for the update. What's your current location and estimated arrival time?",
                "response_id": 1,
                "end_call": False
            }
        elif any(word in utterance_lower for word in ["arrived", "here", "at the dock", "destination"]):
            return {
                "response": "Perfect! Are you already unloading or still waiting to get into a dock? What door are you in?",
                "response_id": 1,
                "end_call": False
            }
        elif any(word in utterance_lower for word in ["delayed", "late", "behind", "stuck"]):
            return {
                "response": "I understand there's a delay. What's causing the delay and when do you expect to arrive?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "Could you give me a bit more detail about your current situation? Are you driving, at your destination, or experiencing any delays?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "location_eta":
        if summary.get("delay_reason") != "None":
            return {
                "response": "Thanks for the location and ETA. I see there might be some delays. Any issues with your load or equipment?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "Perfect, thanks for the update. Any concerns with your load or truck I should know about?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "arrival_details":
        if "unloading" in utterance_lower or "door" in utterance_lower:
            return {
                "response": "Excellent. How's the unloading process going? Any issues with the receiver?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "Good to hear you've arrived. Are you unloading or waiting for a dock assignment?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "delay_details":
        return {
            "response": "I understand about the delay. Keep us updated if anything changes. Any other concerns about your load?",
            "response_id": 1,
            "end_call": False
        }
    
    elif current_phase == "clarification":
        attempts = conversation_state.get("clarification_attempts", 0)
        if attempts >= 2:
            return {
                "response": "I'll make a note about your status. Please contact dispatch if you need assistance. Drive safely!",
                "response_id": 1,
                "end_call": True
            }
        else:
            return {
                "response": "I want to make sure I have all the details. Can you tell me more about your current situation?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "wrap_up":
        return {
            "response": "Thank you for the detailed update. Drive safely and remember to submit your POD when you complete the load. Contact us if anything changes!",
            "response_id": 1,
            "end_call": True
        }
    
    return {
        "response": "Could you please give me a quick status update on your current situation?",
        "response_id": 1,
        "end_call": False
    }

def generate_emergency_protocol_response(utterance: str, transcript: str, call_request: dict, 
                                       summary: dict, conversation_state: Dict[str, Any]) -> dict:
    driver_name = call_request.get("driverName", "")
    load_number = call_request.get("loadNumber", "")
    current_phase = conversation_state.get("phase", "greeting")
    utterance_lower = utterance.lower()
    
    if current_phase == "greeting" or not transcript or len(transcript.split()) < 10:
        return {
            "response": f"Hi {driver_name}, this is Emergency Dispatch calling about load {load_number}. I need to check on your status immediately. Are you safe and do you need any emergency assistance?",
            "response_id": 1,
            "end_call": False
        }
    
    emergency_detected = detect_emergency(utterance_lower, transcript)
    if emergency_detected:
        return {
            "response": "Emergency detected. Is everyone safe? Any injuries that need immediate medical attention?",
            "response_id": 1,
            "end_call": False
        }
    
    elif current_phase == "status_inquiry":
        if any(word in utterance_lower for word in ["fine", "good", "okay", "safe", "no problem"]):
            return {
                "response": "Good to hear you're safe. What's your current status - are you driving, arrived at destination, or experiencing any delays?",
                "response_id": 1,
                "end_call": False
            }
        elif any(word in utterance_lower for word in ["driving", "on the road"]):
            return {
                "response": "Understood. What's your exact location? Any mechanical issues or safety concerns?",
                "response_id": 1,
                "end_call": False
            }
        elif any(word in utterance_lower for word in ["arrived", "here", "destination"]):
            return {
                "response": "Good. Any issues with unloading or receiver? Load secure?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "I need to confirm your safety status. Are you and your load secure with no immediate concerns?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase in ["location_eta", "arrival_details", "delay_details"]:
        return {
            "response": "Thank you for the update. No emergency assistance needed then. Continue with your delivery and contact us immediately if any situation changes.",
            "response_id": 1,
            "end_call": True
        }
    
    elif current_phase == "wrap_up":
        return {
            "response": "Emergency protocol complete - no immediate concerns. Drive safely and contact emergency dispatch immediately if any situation changes. Stay vigilant!",
            "response_id": 1,
            "end_call": True
        }
    
    return {
        "response": "I need to confirm your safety status. Are there any immediate concerns or emergencies I should be aware of?",
        "response_id": 1,
        "end_call": False
    }

def generate_general_response(utterance: str, transcript: str, call_request: dict, 
                            summary: dict, conversation_state: Dict[str, Any]) -> dict:
    driver_name = call_request.get("driverName", "")
    load_number = call_request.get("loadNumber", "")
    current_phase = conversation_state.get("phase", "greeting")
    utterance_lower = utterance.lower()
    
    if current_phase == "greeting" or not transcript or len(transcript.split()) < 10:
        return {
            "response": f"Hi {driver_name}! This is Dispatch with a check call on load {load_number}. Can you give me an update on your status?",
            "response_id": 1,
            "end_call": False
        }
    
    elif current_phase == "status_inquiry":
        if any(word in utterance_lower for word in ["driving", "on the road", "en route", "heading"]):
            return {
                "response": "Great, thanks for the update. What's your current location and estimated arrival time?",
                "response_id": 1,
                "end_call": False
            }
        elif any(word in utterance_lower for word in ["arrived", "here", "at the dock", "destination"]):
            return {
                "response": "Perfect! Are you already unloading or still waiting to get into a dock? What's your unloading status?",
                "response_id": 1,
                "end_call": False
            }
        elif any(word in utterance_lower for word in ["delayed", "late", "behind", "stuck"]):
            return {
                "response": "I understand there's a delay. What's causing the delay and what's your new estimated arrival time?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "I want to make sure I understand correctly. Are you currently driving, have you arrived at your destination, or are you delayed somewhere?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "location_eta":
        if summary.get("delay_reason") != "None":
            return {
                "response": "Thanks for the location and ETA. I see there might be some delays. Is everything okay with the load and truck?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "Perfect, thanks for the update. Are there any issues or concerns I should know about with your load or equipment?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "arrival_details":
        if "unloading" in utterance_lower or "door" in utterance_lower:
            return {
                "response": "Excellent. How's the unloading process going? Any issues with the receiver or paperwork?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "Good to hear you've arrived. Have you started unloading yet, or are you still waiting to get assigned to a dock?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "delay_details":
        return {
            "response": "I understand about the delay. Keep us updated if anything changes. Is there anything else I should know about your load or situation?",
            "response_id": 1,
            "end_call": False
        }
    
    elif current_phase == "clarification":
        attempts = conversation_state.get("clarification_attempts", 0)
        if attempts >= 2:
            return {
                "response": "I'll make a note about your status. Please contact dispatch if you need any assistance with your load. Drive safely!",
                "response_id": 1,
                "end_call": True
            }
        else:
            return {
                "response": "I'm having trouble hearing you clearly. Could you please repeat your current status - are you driving, arrived, or delayed?",
                "response_id": 1,
                "end_call": False
            }
    
    elif current_phase == "wrap_up":
        if len(utterance.split()) <= 2 and utterance_lower in ["yeah", "ok", "sure", "no", "yes", "fine"]:
            return {
                "response": "Thanks for the update. Just to confirm - do you need any assistance from dispatch, and do you have any other concerns about your load?",
                "response_id": 1,
                "end_call": False
            }
        else:
            return {
                "response": "Thank you for the comprehensive update. Drive safely and remember to submit your proof of delivery when you complete the load. Contact us if anything changes!",
                "response_id": 1,
                "end_call": True
            }
    
    return {
        "response": "I want to make sure I have all the details. Could you please give me a quick status update on your current situation?",
        "response_id": 1,
        "end_call": False
    }

def default_response() -> dict:
    return {
        "response": "Hello! This is Dispatch calling for a status update. Can you tell me your current location and estimated arrival time?",
        "response_id": 1,
        "end_call": False
    }