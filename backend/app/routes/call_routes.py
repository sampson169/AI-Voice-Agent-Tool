from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import CallRequest, CallResult
from app.services.retell_service import retell_service
from app.database.supabase import supabase_client
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/calls", tags=["calls"])

@router.post("/web")
async def create_web_call(call_request: CallRequest):
    """Create a web call specifically"""
    try:
        call_request.call_type = "web"
        return await start_call(call_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating web call: {str(e)}")

@router.post("/phone")
async def create_phone_call(call_request: CallRequest):
    """Create a phone call specifically"""
    try:
        call_request.call_type = "phone"
        return await start_call(call_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating phone call: {str(e)}")

@router.post("/start")
async def start_call(call_request: CallRequest):
    try:
        call_id = str(uuid.uuid4())
        
        from app.core.config import settings
        if not call_request.agent_id or call_request.agent_id in ['default', 'default-logistics-agent']:
            call_request.agent_id = 'default-logistics-agent'
            
            existing_agent = await supabase_client.get_agent_config('default-logistics-agent')
            if not existing_agent:
                from app.services.prompt_templates import LogisticsPromptTemplates
                template = LogisticsPromptTemplates.get_scenario_template("general")
                
                default_agent = {
                    "id": "default-logistics-agent",
                    "name": template["name"],
                    "prompt": template["prompt"],
                    "scenario_type": "general",
                    "voice_settings": template["voice_settings"],
                    "emergency_phrases": template["emergency_phrases"],
                    "structured_fields": template["structured_fields"],
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                await supabase_client.create_agent_config(default_agent)
            
            retell_agent_id = settings.retell_agent_id or 'agent_fa51b58953a177984c9e173910'
        else:
            retell_agent_id = settings.retell_agent_id or call_request.agent_id
        
        original_agent_id = call_request.agent_id
        call_request.agent_id = retell_agent_id
        
        if call_request.call_type == "phone":
            retell_response = await retell_service.create_phone_call(call_request)
        else:
            retell_response = await retell_service.create_web_call(call_request)
        
        call_request.agent_id = original_agent_id
        
        if retell_response and "error" not in retell_response:
            retell_call_id = retell_response.get("call_id", call_id)
            
            call_data = {
                "id": call_id,
                "retell_call_id": retell_call_id,
                "call_request": call_request.dict(),
                "transcript": "",
                "summary": {},
                "conversation_state": {
                    "phase": "greeting",
                    "emergency_detected": False,
                    "clarification_attempts": 0,
                    "scenario_type": "general"
                },
                "timestamp": datetime.utcnow().isoformat(),
                "duration": 0
            }
            
            await supabase_client.create_call_result(call_data)
            
            response = {
                "call_id": call_id,
                "retell_call_id": retell_call_id,
                "status": "initiated",
                "web_call_link": retell_response.get("web_call_link"),
                "access_token": retell_response.get("access_token")
            }
            
            return response
        else:
            error_msg = retell_response.get("error", "Unknown error") if retell_response else "Failed to create call"
            error_details = retell_response.get("details", "") if retell_response else ""
            full_error = f"{error_msg}. Details: {error_details}" if error_details else error_msg
            raise HTTPException(status_code=500, detail=full_error)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting call: {str(e)}")

@router.get("/{call_id}/result", response_model=CallResult)
async def get_call_result(call_id: str):
    """Get call result by ID"""
    try:
        result = await supabase_client.get_call_result(call_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Call result not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching call result: {str(e)}")

@router.get("/")
async def get_all_call_results():
    """Get all call results"""
    try:
        results = await supabase_client.get_all_call_results()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching call results: {str(e)}")