from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from ..database.performance_monitor import get_performance_monitor, DatabasePerformanceMonitor


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/performance", tags=["performance"])


async def get_monitor() -> DatabasePerformanceMonitor:
    """Dependency to get performance monitor"""
    monitor = get_performance_monitor()
    if not monitor:
        raise HTTPException(status_code=503, detail="Performance monitor not initialized")
    return monitor


@router.get("/dashboard")
async def get_performance_dashboard(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get comprehensive performance dashboard data"""
    try:
        dashboard_data = await monitor.get_performance_dashboard()
        return {
            'success': True,
            'data': dashboard_data,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_current_metrics(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get current database performance metrics"""
    try:
        metrics = await monitor._collect_performance_metrics()
        return {
            'success': True,
            'metrics': {
                name: {
                    'value': metric.current_value,
                    'unit': metric.unit,
                    'status': metric.status.value,
                    'threshold_warning': metric.threshold_warning,
                    'threshold_critical': metric.threshold_critical,
                    'recommendation': metric.recommendation
                } for name, metric in metrics.items()
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting current metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/queries/slow")
async def get_slow_queries(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get slow query analysis"""
    try:
        slow_queries = await monitor._analyze_query_performance()
        return {
            'success': True,
            'queries': [
                {
                    'query_hash': query.query_hash,
                    'query_text': query.query_text,
                    'execution_count': query.execution_count,
                    'total_time_ms': query.total_time_ms,
                    'mean_time_ms': query.mean_time_ms,
                    'max_time_ms': query.max_time_ms,
                    'rows_affected': query.rows_affected,
                    'performance_impact': query.performance_impact
                } for query in slow_queries
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/indexes")
async def get_index_analysis(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get index usage analysis"""
    try:
        index_analysis = await monitor._check_index_usage()
        return {
            'success': True,
            'indexes': [
                {
                    'index_name': idx.index_name,
                    'table_name': idx.table_name,
                    'index_size': idx.index_size,
                    'usage_count': idx.usage_count,
                    'last_used': idx.last_used.isoformat() if idx.last_used else None,
                    'efficiency_score': idx.efficiency_score,
                    'recommendation': idx.recommendation
                } for idx in index_analysis
            ],
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting index analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recommendations")
async def get_optimization_recommendations(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get optimization recommendations"""
    try:
        await monitor._update_recommendations()
        
        return {
            'success': True,
            'recommendations': [
                {
                    'optimization_type': rec.optimization_type.value,
                    'priority': rec.priority,
                    'description': rec.description,
                    'estimated_impact': rec.estimated_impact,
                    'implementation_steps': rec.implementation_steps,
                    'estimated_time_savings': rec.estimated_time_savings
                } for rec in monitor.optimization_recommendations
            ],
            'last_analysis': monitor.last_analysis_time.isoformat() if monitor.last_analysis_time else None,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report")
async def get_optimization_report(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get comprehensive optimization report"""
    try:
        report = await monitor.get_optimization_report()
        return {
            'success': True,
            'report': report,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting optimization report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_performance_trends(
    hours: int = 24,
    monitor: DatabasePerformanceMonitor = Depends(get_monitor)
) -> Dict[str, Any]:
    """Get performance trends over time"""
    try:
        max_points = hours * 12
        trends = monitor.performance_history[-max_points:] if monitor.performance_history else []
        
        trend_summary = {}
        if trends:
            for metric_name in ['connection_usage', 'cache_hit_ratio', 'table_bloat']:
                values = []
                for point in trends:
                    if metric_name in point['metrics']:
                        values.append(point['metrics'][metric_name]['value'])
                
                if values:
                    trend_summary[metric_name] = {
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'current': values[-1] if values else 0,
                        'trend': 'improving' if len(values) > 1 and values[-1] < values[0] else 'stable'
                    }
        
        return {
            'success': True,
            'trends': trends,
            'summary': trend_summary,
            'data_points': len(trends),
            'hours_covered': len(trends) * 5 / 60,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize/{optimization_type}")
async def execute_optimization(
    optimization_type: str,
    monitor: DatabasePerformanceMonitor = Depends(get_monitor)
) -> Dict[str, Any]:
    """Execute specific optimization"""
    try:
        valid_types = ['table_maintenance', 'index_cleanup', 'connection_optimization']
        if optimization_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid optimization type. Valid types: {valid_types}"
            )
        
        result = await monitor.execute_optimization(optimization_type)
        
        return {
            'success': result['success'],
            'optimization_type': optimization_type,
            'actions_taken': result['actions_taken'],
            'error': result.get('error'),
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error executing optimization {optimization_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def get_performance_health(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get overall performance health status"""
    try:
        current_metrics = await monitor._collect_performance_metrics()
        
        # Calculate health scores
        health_scores = []
        status_counts = {'excellent': 0, 'good': 0, 'warning': 0, 'critical': 0}
        
        for metric in current_metrics.values():
            status = metric.status.value
            status_counts[status] += 1
            
            if status == 'excellent':
                health_scores.append(100)
            elif status == 'good':
                health_scores.append(80)
            elif status == 'warning':
                health_scores.append(60)
            else:  # critical
                health_scores.append(30)
        
        overall_score = sum(health_scores) / len(health_scores) if health_scores else 50
        
        if overall_score >= 90:
            overall_status = 'excellent'
        elif overall_score >= 75:
            overall_status = 'good'
        elif overall_score >= 60:
            overall_status = 'warning'
        else:
            overall_status = 'critical'
        
        return {
            'success': True,
            'health': {
                'overall_score': round(overall_score, 1),
                'overall_status': overall_status,
                'metric_counts': status_counts,
                'total_metrics': len(current_metrics),
                'recommendations_count': len(monitor.optimization_recommendations),
                'monitoring_active': monitor.monitoring_active
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting performance health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_monitor_status(monitor: DatabasePerformanceMonitor = Depends(get_monitor)) -> Dict[str, Any]:
    """Get performance monitor status"""
    try:
        return {
            'success': True,
            'status': {
                'monitoring_active': monitor.monitoring_active,
                'last_analysis': monitor.last_analysis_time.isoformat() if monitor.last_analysis_time else None,
                'recommendations_count': len(monitor.optimization_recommendations),
                'history_points': len(monitor.performance_history),
                'connection_pool_active': monitor.connection_pool is not None
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting monitor status: {e}")
        raise HTTPException(status_code=500, detail=str(e))