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
    
    async def create_rtvi_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new RTVI event for analytics"""
        result = self.client.table("rtvi_events").insert(event_data).execute()
        return result.data[0] if result.data else None
    
    async def get_rtvi_events(self, call_id: str) -> List[Dict[str, Any]]:
        """Get all RTVI events for a specific call"""
        result = self.client.table("rtvi_events").select("*").eq("call_id", call_id).order("timestamp", desc=False).execute()
        return result.data
    
    async def get_rtvi_events_by_type(self, event_type: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get RTVI events by type across all calls"""
        result = self.client.table("rtvi_events").select("*").eq("event_type", event_type).order("timestamp", desc=True).limit(limit).execute()
        return result.data
    
    async def create_call_metrics(self, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update call metrics"""
        result = self.client.table("call_metrics").upsert(metrics_data).execute()
        return result.data[0] if result.data else None
    
    async def get_call_metrics(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call metrics by call ID"""
        result = self.client.table("call_metrics").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None
    
    async def get_analytics_summary(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get analytics summary using the view"""
        result = self.client.table("analytics_summary").select("*").order("start_time", desc=True).limit(limit).execute()
        return result.data
    
    async def get_analytics_aggregations(self, start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """Get analytics aggregations for a date range"""
        query = self.client.table("daily_analytics").select("*")
        
        if start_date:
            query = query.gte("date_range_start", start_date)
        if end_date:
            query = query.lte("date_range_end", end_date)
        
        result = query.order("date_range_start", desc=True).execute()
        return result.data
    
    async def compute_daily_analytics(self, target_date: str = None) -> bool:
        """Trigger daily analytics computation"""
        try:
            if target_date:
                result = self.client.rpc("compute_daily_analytics", {"target_date": target_date}).execute()
            else:
                result = self.client.rpc("compute_daily_analytics").execute()
            return True
        except Exception as e:
            return False
    
    def get_dashboard_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get aggregated metrics for dashboard display"""
        try:
            from datetime import datetime, timedelta
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            cutoff_iso = cutoff_date.isoformat()
            
            result = self.client.table("call_results").select("*").gte("timestamp", cutoff_iso).execute()
            call_results = result.data
            
            if len(call_results) == 0:
                all_result = self.client.table("call_results").select("*").execute()
                all_calls = all_result.data
            
            total_calls = len(call_results)
            total_duration = 0
            total_tokens = 0
            total_interruptions = 0
            emergency_calls = 0
            outcomes = {}
            
            for call in call_results:
                duration = call.get('duration', 0)
                total_duration += duration
                
                summary = call.get('summary', {})
                tokens = summary.get('tokens_used', 0)
                if isinstance(tokens, int):
                    total_tokens += tokens
                
                # Interruptions (if available in summary)
                interruptions = summary.get('interruptions', 0)
                if isinstance(interruptions, int):
                    total_interruptions += interruptions
                
                # Emergency detection
                conversation_state = call.get('conversation_state', {})
                if conversation_state.get('emergency_detected', False):
                    emergency_calls += 1
                
                # Call outcomes
                outcome = summary.get('call_outcome', 'Unknown')
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            # Calculate averages
            avg_duration = total_duration / total_calls if total_calls > 0 else 0
            avg_tokens = total_tokens / total_calls if total_calls > 0 else 0
            successful_calls = total_calls - emergency_calls
            
            return {
                "total_calls": total_calls,
                "avg_call_duration": round(avg_duration, 2),
                "total_interruptions": total_interruptions,
                "total_tokens": total_tokens,
                "avg_tokens_per_call": round(avg_tokens, 2),
                "outcomes": outcomes,
                "event_types": {},  # This would need RTVI events
                "emergency_calls": emergency_calls,
                "successful_calls": successful_calls
            }
            
        except Exception as e:
            return {
                "total_calls": -999,
                "avg_call_duration": 0,
                "total_interruptions": 0,
                "total_tokens": 0,
                "avg_tokens_per_call": 0,
                "outcomes": {},
                "event_types": {},
                "emergency_calls": 0,
                "successful_calls": 0
            }

supabase_client = SupabaseClient()