from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.models.schemas import CallRequest, CallResult
from app.services.retell_service import retell_service
from app.database.supabase import supabase_client
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/calls", tags=["calls"])

@router.post("/start")
async def start_call(call_request: CallRequest):
    try:
        call_id = str(uuid.uuid4())
        
        from app.core.config import settings
        if not call_request.agent_id or call_request.agent_id in ['default', 'default-logistics-agent']:
            call_request.agent_id = settings.retell_agent_id or 'agent_b4902d2c6973a595dc4cf5ad55'
        
        print(f"🎯 Starting {call_request.call_type} call with agent_id: {call_request.agent_id}")
        
        if call_request.call_type == "phone":
            retell_response = await retell_service.create_phone_call(call_request)
        else:
            retell_response = await retell_service.create_web_call(call_request)
        
        print(f"📞 Retell response: {retell_response}")
        
        if retell_response and "error" not in retell_response:
            retell_call_id = retell_response.get("call_id", call_id)
            
            call_data = {
                "id": call_id,
                "retell_call_id": retell_call_id,
                "call_request": call_request.dict(),
                "transcript": "",
                "summary": {},
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
            
            print(f"✅ Call started successfully: {response}")
            return response
        else:
            error_msg = retell_response.get("error", "Unknown error") if retell_response else "Failed to create call"
            error_details = retell_response.get("details", "") if retell_response else ""
            full_error = f"{error_msg}. Details: {error_details}" if error_details else error_msg
            print(f"❌ Call start failed: {full_error}")
            raise HTTPException(status_code=500, detail=full_error)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Unexpected error starting call: {str(e)}")
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