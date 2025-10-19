from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import CallRequest, CallResult
from app.pipecat.pipecat_service import pipecat_service
from app.services.retell_service import retell_service  # Keep for backwards compatibility
from app.database.supabase import supabase_client
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
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
        logger.info(f"Received call request: {call_request}")
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
        
        # Use PIPECAT instead of Retell
        logger.info(f"Creating PIPECAT call of type: {call_request.call_type}")
        if call_request.call_type == "phone":
            pipecat_response = await pipecat_service.create_phone_call(call_request)
        else:
            pipecat_response = await pipecat_service.create_web_call(call_request)
        
        logger.info(f"PIPECAT response: {pipecat_response}")
        
        if pipecat_response and "error" not in pipecat_response:
            pipecat_call_id = pipecat_response.get("call_id", call_id)
            
            call_data = {
                "id": call_id,
                "retell_call_id": pipecat_call_id,  # Keep field name for compatibility
                "call_request": call_request.dict(),
                "transcript": "",
                "summary": {},
                "conversation_state": {
                    "phase": "greeting",
                    "emergency_detected": False,
                    "clarification_attempts": 0,
                    "scenario_type": getattr(call_request, 'scenario_type', 'general'),
                    "pipecat_call": True,  # Mark as PIPECAT call in conversation state
                    "analytics_enabled": True
                },
                "timestamp": datetime.utcnow().isoformat(),
                "duration": 0
            }
            
            await supabase_client.create_call_result(call_data)
            
            response = {
                "call_id": call_id,
                "pipecat_call_id": pipecat_call_id,
                "status": "initiated",
                "web_call_link": pipecat_response.get("web_call_link"),
                "access_token": pipecat_response.get("access_token"),
                "phone_number": pipecat_response.get("phone_number")
            }
            
            logger.info(f"Returning successful response: {response}")
            return response
        else:
            error_msg = pipecat_response.get("error", "Unknown error") if pipecat_response else "Failed to create call"
            logger.error(f"PIPECAT call creation failed: {error_msg}")
            raise HTTPException(status_code=500, detail=error_msg)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting call: {str(e)}", exc_info=True)
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