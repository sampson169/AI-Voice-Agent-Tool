from supabase import create_client, Client
from app.core.config import settings
from typing import Dict, Any, List, Optional
import asyncio

class SupabaseClient:
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )
    
    async def create_agent_config(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent configuration"""
        result = self.client.table("agent_configs").insert(config_data).execute()
        return result.data[0] if result.data else None
    
    async def get_agent_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """Get agent configuration by ID"""
        result = self.client.table("agent_configs").select("*").eq("id", config_id).execute()
        return result.data[0] if result.data else None
    
    async def get_all_agent_configs(self) -> List[Dict[str, Any]]:
        """Get all agent configurations"""
        result = self.client.table("agent_configs").select("*").execute()
        return result.data
    
    async def update_agent_config(self, config_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent configuration"""
        result = self.client.table("agent_configs").update(updates).eq("id", config_id).execute()
        return result.data[0] if result.data else None
    
    async def create_call_result(self, call_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store call result in database"""
        result = self.client.table("call_results").insert(call_data).execute()
        return result.data[0] if result.data else None
    
    async def get_call_result(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call result by ID"""
        result = self.client.table("call_results").select("*").eq("id", call_id).execute()
        return result.data[0] if result.data else None
    
    async def get_all_call_results(self) -> List[Dict[str, Any]]:
        result = self.client.table("call_results").select("*").order("timestamp", desc=True).execute()
        return result.data
    
    async def update_call_result(self, call_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        result = self.client.table("call_results").update(updates).eq("id", call_id).execute()
        return result.data[0] if result.data else None
    
    async def test_connection(self) -> bool:
        try:
            result = self.client.table("call_results").select("*").limit(1).execute()
            return True
        except Exception as e:
            error_msg = str(e).lower()            
            if "does not exist" in error_msg or "relation" in error_msg or "not found" in error_msg:
                return True
            
            if "unauthorized" in error_msg or "forbidden" in error_msg or "invalid" in error_msg:
                return False
            
            return True

supabase_client = SupabaseClient()