import httpx
import json
from app.core.config import settings
from typing import Dict, Any, Optional
from app.models.schemas import CallRequest

class RetellService:
    def __init__(self):
        self.base_url = settings.retell_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.retell_api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_phone_call(self, call_request: CallRequest, from_number: str = "+15551234567") -> Dict[str, Any]:
        payload = {
            "from_number": from_number,
            "to_number": call_request.phone_number,
            "agent_id": call_request.agent_id,
            "override_agent_id": call_request.agent_id,
            "retell_llm_dynamic_variables": {
                "driver_name": call_request.driver_name,
                "load_number": call_request.load_number
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/call",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    return {"error": f"API Error: {response.status_code}", "details": response.text}
                    
            except Exception as e:
                return {"error": "Connection failed", "details": str(e)}
    
    async def create_web_call(self, call_request: CallRequest) -> Dict[str, Any]:
        payload = {
            "agent_id": call_request.agent_id,
            "retell_llm_dynamic_variables": {
                "driver_name": call_request.driver_name,
                "load_number": call_request.load_number
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/create-web-call",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    response_data = response.json()
                    print(f"✅ Web call created successfully: {response_data}")
                    return response_data
                else:
                    error_details = {
                        "error": f"Web Call API Error: {response.status_code}", 
                        "details": response.text,
                        "status_code": response.status_code
                    }
                    print(f"❌ Web call failed: {error_details}")
                    return error_details
                    
            except Exception as e:
                error_details = {"error": "Web call connection failed", "details": str(e)}
                print(f"❌ Web call exception: {error_details}")
                return error_details
    
    async def get_call_details(self, call_id: str) -> Optional[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/get-call/{call_id}",
                    headers=self.headers,
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return None
                    
            except Exception:
                return None

    async def create_agent(self, agent_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        payload = {
            "llm_websocket_url": "wss://your-webhook-url.com/webhook/retell",
            "voice_id": agent_config.get("voice_settings", {}).get("voice_id", "11labs-Adrian"),
            "agent_name": agent_config.get("name", "Logistics Agent"),
            "language": "en-US",
            "response_engine": {
                "type": "retell_llm",
                "llm_id": agent_config.get("id")
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/agent",
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                else:
                    return None
                    
            except Exception:
                return None

retell_service = RetellService()