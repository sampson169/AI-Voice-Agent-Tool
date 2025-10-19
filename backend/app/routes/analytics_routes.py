"""
Analytics API Routes
Provides endpoints for PIPECAT analytics data
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from app.database.supabase import supabase_client

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/dashboard")
async def get_dashboard_metrics(days: int = Query(default=30, ge=1, le=365)):
    """Get dashboard metrics for the specified number of days"""
    try:
        metrics = await supabase_client.get_dashboard_metrics(days)
        return {
            "status": "success",
            "data": metrics,
            "period_days": days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dashboard metrics: {str(e)}")


@router.get("/calls")
async def get_analytics_summary(limit: int = Query(default=50, ge=1, le=200)):
    """Get analytics summary for recent calls"""
    try:
        summary = await supabase_client.get_analytics_summary(limit)
        return {
            "status": "success",
            "data": summary,
            "total_records": len(summary)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics summary: {str(e)}")


@router.get("/events/{call_id}")
async def get_call_events(call_id: str):
    """Get all RTVI events for a specific call"""
    try:
        events = await supabase_client.get_rtvi_events(call_id)
        return {
            "status": "success",
            "call_id": call_id,
            "events": events,
            "total_events": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching call events: {str(e)}")


@router.get("/events")
async def get_events_by_type(
    event_type: str = Query(..., description="Type of RTVI event to filter by"),
    limit: int = Query(default=100, ge=1, le=500)
):
    """Get RTVI events by type across all calls"""
    try:
        events = await supabase_client.get_rtvi_events_by_type(event_type, limit)
        return {
            "status": "success",
            "event_type": event_type,
            "events": events,
            "total_events": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events by type: {str(e)}")


@router.get("/metrics/{call_id}")
async def get_call_metrics(call_id: str):
    """Get detailed metrics for a specific call"""
    try:
        metrics = await supabase_client.get_call_metrics(call_id)
        
        if not metrics:
            raise HTTPException(status_code=404, detail="Call metrics not found")
        
        # Also get events for this call
        events = await supabase_client.get_rtvi_events(call_id)
        
        return {
            "status": "success",
            "call_id": call_id,
            "metrics": metrics,
            "events": events,
            "total_events": len(events)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching call metrics: {str(e)}")


@router.get("/aggregations")
async def get_analytics_aggregations(
    start_date: Optional[str] = Query(default=None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="End date (YYYY-MM-DD)")
):
    """Get analytics aggregations for a date range"""
    try:
        # Default to last 30 days if no dates provided
        if not start_date or not end_date:
            end_date = datetime.utcnow().date().isoformat()
            start_date = (datetime.utcnow().date() - timedelta(days=30)).isoformat()
        
        aggregations = await supabase_client.get_analytics_aggregations(start_date, end_date)
        
        return {
            "status": "success",
            "start_date": start_date,
            "end_date": end_date,
            "aggregations": aggregations,
            "total_periods": len(aggregations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching aggregations: {str(e)}")


@router.post("/compute")
async def compute_daily_analytics(
    target_date: Optional[str] = Query(default=None, description="Target date (YYYY-MM-DD)")
):
    """Trigger daily analytics computation"""
    try:
        success = await supabase_client.compute_daily_analytics(target_date)
        
        if success:
            return {
                "status": "success",
                "message": f"Analytics computed for date: {target_date or 'today'}",
                "target_date": target_date
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to compute analytics")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error computing analytics: {str(e)}")


@router.get("/outcomes")
async def get_call_outcomes_distribution(days: int = Query(default=30, ge=1, le=365)):
    """Get distribution of call outcomes over the specified period"""
    try:
        metrics = await supabase_client.get_dashboard_metrics(days)
        outcomes = metrics.get("outcomes", {})
        
        # Calculate percentages
        total_calls = sum(outcomes.values())
        outcome_distribution = []
        
        for outcome, count in outcomes.items():
            percentage = (count / total_calls * 100) if total_calls > 0 else 0
            outcome_distribution.append({
                "outcome": outcome,
                "count": count,
                "percentage": round(percentage, 2)
            })
        
        return {
            "status": "success",
            "period_days": days,
            "total_calls": total_calls,
            "distribution": outcome_distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching outcome distribution: {str(e)}")


@router.get("/interruptions")
async def get_interruption_analysis(days: int = Query(default=30, ge=1, le=365)):
    """Get interruption analysis data"""
    try:
        # Get calls with interruption data
        summary = await supabase_client.get_analytics_summary(limit=1000)
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_calls = [
            call for call in summary 
            if call.get('start_time') and 
            datetime.fromisoformat(call['start_time'].replace('Z', '+00:00')) >= cutoff_date
        ]
        
        # Analyze interruptions
        total_calls = len(recent_calls)
        total_interruptions = sum(call.get('interruption_count', 0) for call in recent_calls)
        calls_with_interruptions = len([call for call in recent_calls if call.get('interruption_count', 0) > 0])
        
        avg_interruptions_per_call = total_interruptions / total_calls if total_calls > 0 else 0
        interruption_rate = calls_with_interruptions / total_calls * 100 if total_calls > 0 else 0
        
        return {
            "status": "success",
            "period_days": days,
            "total_calls": total_calls,
            "total_interruptions": total_interruptions,
            "calls_with_interruptions": calls_with_interruptions,
            "avg_interruptions_per_call": round(avg_interruptions_per_call, 2),
            "interruption_rate_percentage": round(interruption_rate, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching interruption analysis: {str(e)}")


@router.get("/tokens")
async def get_token_usage_analysis(days: int = Query(default=30, ge=1, le=365)):
    """Get token usage analysis"""
    try:
        metrics = await supabase_client.get_dashboard_metrics(days)
        
        return {
            "status": "success",
            "period_days": days,
            "total_tokens": metrics.get("total_tokens", 0),
            "avg_tokens_per_call": metrics.get("avg_tokens_per_call", 0),
            "total_calls": metrics.get("total_calls", 0),
            "estimated_cost": round(metrics.get("total_tokens", 0) * 0.0001, 4)  # Rough estimate
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching token analysis: {str(e)}")


@router.get("/trends")
async def get_analytics_trends(days: int = Query(default=30, ge=7, le=365)):
    """Get analytics trends over time"""
    try:
        # Get aggregations for the period
        end_date = datetime.utcnow().date().isoformat()
        start_date = (datetime.utcnow().date() - timedelta(days=days)).isoformat()
        
        aggregations = await supabase_client.get_analytics_aggregations(start_date, end_date)
        
        # Process trends
        trends = []
        for agg in sorted(aggregations, key=lambda x: x['date_range_start']):
            trends.append({
                "date": agg['date_range_start'],
                "total_calls": agg.get('total_calls', 0),
                "avg_duration": agg.get('avg_call_duration', 0),
                "interruptions": agg.get('total_interruptions', 0),
                "emergency_calls": agg.get('emergency_calls', 0),
                "tokens_used": agg.get('total_tokens_spent', 0)
            })
        
        return {
            "status": "success",
            "period_days": days,
            "start_date": start_date,
            "end_date": end_date,
            "trends": trends
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")


@router.get("/health")
async def analytics_health_check():
    """Health check for analytics service"""
    try:
        # Test database connection
        test_metrics = await supabase_client.get_dashboard_metrics(1)
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connected": True,
            "message": "Analytics service is operational"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_connected": False,
            "error": str(e)
        }