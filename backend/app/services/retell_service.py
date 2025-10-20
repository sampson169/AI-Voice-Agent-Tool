"""
DEPRECATED: Retell AI Service
This module is being phased out as part of the PIPECAT migration.
Use app.pipecat.pipecat_service instead.
"""

import httpx
import json
from app.core.config import settings
from typing import Dict, Any, Optional
from app.models.schemas import CallRequest
import warnings



class RetellService:
    def __init__(self):
        self.base_url = settings.retell_base_url
        self.headers = {
            "Authorization": f"Bearer {settings.retell_api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_phone_call(self, call_request: CallRequest, from_number: str = "+15551234567") -> Dict[str, Any]:
        from app.database.supabase import supabase_client
        agent_config = await supabase_client.get_agent_config(call_request.agent_id)
        
        dynamic_variables = {
            "driver_name": call_request.driver_name,
            "load_number": call_request.load_number,
            "agent_id": call_request.agent_id
        }
        
        if agent_config:
            dynamic_variables.update({
                "agent_prompt": agent_config.get("prompt", ""),
                "scenario_type": agent_config.get("scenario_type", "general"),
                "emergency_phrases": ",".join(agent_config.get("emergency_phrases", []))
            })
        
        payload = {
            "from_number": from_number,
            "to_number": call_request.phone_number,
            "agent_id": call_request.agent_id,
            "override_agent_id": call_request.agent_id,
            "retell_llm_dynamic_variables": dynamic_variables
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
        from app.database.supabase import supabase_client
        agent_config = await supabase_client.get_agent_config(call_request.agent_id)
        
        dynamic_variables = {
            "driver_name": call_request.driver_name,
            "load_number": call_request.load_number,
            "agent_id": call_request.agent_id
        }
        
        if agent_config:
            dynamic_variables.update({
                "agent_prompt": agent_config.get("prompt", ""),
                "scenario_type": agent_config.get("scenario_type", "general"),
                "emergency_phrases": ",".join(agent_config.get("emergency_phrases", []))
            })
        
        payload = {
            "agent_id": call_request.agent_id,
            "retell_llm_dynamic_variables": dynamic_variables
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
                    return response_data
                else:
                    error_details = {
                        "error": f"Web Call API Error: {response.status_code}", 
                        "details": response.text,
                        "status_code": response.status_code
                    }
                    return error_details
                    
            except Exception as e:
                error_details = {"error": "Web call connection failed", "details": str(e)}
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
        """Create a Retell agent configured to use our webhook for responses"""
        from app.core.config import settings
        
        webhook_url = settings.retell_webhook_url or f"https://your-domain.com/api/webhook/retell"
        ws_url = webhook_url.replace("https://", "wss://").replace("http://", "ws://")
        
        payload = {
            "llm_websocket_url": ws_url,
            "voice_id": agent_config.get("voice_settings", {}).get("voice_id", "11labs-Adrian"),
            "agent_name": agent_config.get("name", "Logistics Dispatcher"),
            "language": "en-US",
            "response_engine": {
                "type": "retell_llm",
                "llm_id": agent_config.get("id", "custom-logistics-agent")
            },
            "voice_temperature": agent_config.get("voice_settings", {}).get("temperature", 0.7),
            "voice_speed": agent_config.get("voice_settings", {}).get("speed", 1.0),
            "enable_backchannel": agent_config.get("voice_settings", {}).get("backchanneling", True),
            "interruption_sensitivity": self._map_interruption_sensitivity(
                agent_config.get("voice_settings", {}).get("interruption_sensitivity", "medium")
            ),
            "ambient_sound": None,
            "webhook_url": webhook_url,
            "responsiveness": 1.0,
            "interruption_threshold": 100
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
                    result = response.json()
                    return result
                else:
                    return None
                    
            except Exception as e:
                return None
    
    def _map_interruption_sensitivity(self, sensitivity: str) -> int:
        """Map our interruption sensitivity to Retell's scale"""
        mapping = {
            "low": 50,
            "medium": 100, 
            "high": 150
        }
        return mapping.get(sensitivity, 100)

retell_service = RetellService()