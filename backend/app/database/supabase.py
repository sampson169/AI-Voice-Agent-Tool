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
    
    # PIPECAT Analytics Methods
    
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
            print(f"Error computing daily analytics: {e}")
            return False
    
    async def get_dashboard_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get aggregated metrics for dashboard display"""
        try:
            # Get recent call metrics
            result = self.client.table("call_metrics").select("*").gte("start_time", f"now() - interval '{days} days'").execute()
            call_metrics = result.data
            
            # Get recent RTVI events
            events_result = self.client.table("rtvi_events").select("*").gte("timestamp", f"now() - interval '{days} days'").execute()
            rtvi_events = events_result.data
            
            # Calculate aggregated metrics
            total_calls = len(call_metrics)
            avg_duration = sum(float(m.get('duration_seconds', 0)) for m in call_metrics) / total_calls if total_calls > 0 else 0
            total_interruptions = sum(int(m.get('interruption_count', 0)) for m in call_metrics)
            total_tokens = sum(int(m.get('total_tokens', 0)) for m in call_metrics)
            
            # Count outcomes
            outcomes = {}
            for metric in call_metrics:
                outcome = metric.get('final_outcome', 'Unknown')
                outcomes[outcome] = outcomes.get(outcome, 0) + 1
            
            # Count event types
            event_types = {}
            for event in rtvi_events:
                event_type = event.get('event_type', 'unknown')
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            return {
                "total_calls": total_calls,
                "avg_call_duration": round(avg_duration, 2),
                "total_interruptions": total_interruptions,
                "total_tokens": total_tokens,
                "avg_tokens_per_call": round(total_tokens / total_calls, 2) if total_calls > 0 else 0,
                "outcomes": outcomes,
                "event_types": event_types,
                "emergency_calls": outcomes.get("Emergency Escalation", 0),
                "successful_calls": total_calls - outcomes.get("Unknown", 0)
            }
            
        except Exception as e:
            print(f"Error getting dashboard metrics: {e}")
            return {
                "total_calls": 0,
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