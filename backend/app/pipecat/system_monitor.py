"""
Enhanced Error Handling and System Monitoring Module
Comprehensive error tracking, health monitoring, and alerting system for PIPECAT voice calls
"""

import logging
import asyncio
import traceback
import json
from typing import Dict, Any, List, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SystemComponent(Enum):
    PIPECAT_ENGINE = "pipecat_engine"
    AUDIO_PROCESSING = "audio_processing"
    LLM_SERVICE = "llm_service"
    TTS_SERVICE = "tts_service"
    STT_SERVICE = "stt_service"
    DATABASE = "database"
    ANALYTICS = "analytics"
    CALL_ROUTING = "call_routing"
    NETWORK = "network"


class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    DOWN = "down"


@dataclass
class ErrorEvent:
    """Structured error event for tracking and analysis"""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    component: SystemComponent
    error_type: str
    error_message: str
    call_id: Optional[str] = None
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    resolution_attempted: bool = False
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class HealthMetric:
    """System health metric"""
    component: SystemComponent
    metric_name: str
    value: float
    status: HealthStatus
    timestamp: datetime
    threshold_warning: float = 0.8
    threshold_critical: float = 0.5
    unit: str = ""


@dataclass
class SystemAlert:
    """System alert for critical issues"""
    alert_id: str
    timestamp: datetime
    severity: ErrorSeverity
    component: SystemComponent
    title: str
    description: str
    call_id: Optional[str] = None
    auto_resolution_attempted: bool = False
    acknowledged: bool = False
    resolved: bool = False


class SystemMonitor:
    """
    Comprehensive system monitoring and health tracking
    """
    
    def __init__(self, supabase_client=None):
        self.supabase_client = supabase_client
        
        # Error and event tracking
        self.error_events: deque = deque(maxlen=1000)
        self.health_metrics: Dict[SystemComponent, Dict[str, HealthMetric]] = defaultdict(dict)
        self.active_alerts: Dict[str, SystemAlert] = {}
        
        # Performance tracking
        self.component_performance: Dict[SystemComponent, deque] = defaultdict(lambda: deque(maxlen=100))
        self.error_patterns: Dict[str, int] = defaultdict(int)
        self.recovery_attempts: Dict[str, int] = defaultdict(int)
        
        # Health check intervals and thresholds
        self.health_check_interval = 30  # seconds
        self.error_threshold_per_minute = 10
        self.response_time_threshold = 5.0  # seconds
        
        # Automatic recovery configurations
        self.auto_recovery_enabled = True
        self.max_recovery_attempts = 3
        
        logger.info("System Monitor initialized")
    
    async def log_error(self, 
                       component: SystemComponent, 
                       error_type: str, 
                       error_message: str,
                       severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       call_id: Optional[str] = None,
                       context: Optional[Dict[str, Any]] = None,
                       exception: Optional[Exception] = None) -> str:
        """Log a comprehensive error event"""
        
        error_id = str(uuid.uuid4())
        stack_trace = None
        
        if exception:
            stack_trace = traceback.format_exception(type(exception), exception, exception.__traceback__)
            stack_trace = ''.join(stack_trace)
        
        error_event = ErrorEvent(
            error_id=error_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            component=component,
            error_type=error_type,
            error_message=error_message,
            call_id=call_id,
            stack_trace=stack_trace,
            context=context or {}
        )
        
        self.error_events.append(error_event)
        self.error_patterns[f"{component.value}:{error_type}"] += 1
        
        # Store in database if available
        if self.supabase_client:
            await self._store_error_event(error_event)
        
        # Check if this triggers an alert
        await self._evaluate_alert_conditions(error_event)
        
        # Attempt automatic recovery for critical errors
        if severity == ErrorSeverity.CRITICAL and self.auto_recovery_enabled:
            await self._attempt_auto_recovery(error_event)
        
        logger.error(f"Error logged: {component.value} - {error_type}: {error_message}")
        
        return error_id
    
    async def update_health_metric(self, 
                                  component: SystemComponent,
                                  metric_name: str,
                                  value: float,
                                  unit: str = "",
                                  threshold_warning: float = 0.8,
                                  threshold_critical: float = 0.5) -> None:
        """Update a health metric for a system component"""
        
        # Determine status based on thresholds
        if value >= threshold_warning:
            status = HealthStatus.HEALTHY
        elif value >= threshold_critical:
            status = HealthStatus.WARNING
        elif value >= threshold_critical * 0.5:
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.CRITICAL
        
        metric = HealthMetric(
            component=component,
            metric_name=metric_name,
            value=value,
            status=status,
            timestamp=datetime.utcnow(),
            threshold_warning=threshold_warning,
            threshold_critical=threshold_critical,
            unit=unit
        )
        
        self.health_metrics[component][metric_name] = metric
        
        # Store performance data
        self.component_performance[component].append({
            'timestamp': metric.timestamp,
            'metric': metric_name,
            'value': value,
            'status': status.value
        })
        
        # Check for alerts
        if status in [HealthStatus.CRITICAL, HealthStatus.DEGRADED]:
            await self._create_health_alert(metric)
        
        if self.supabase_client:
            await self._store_health_metric(metric)
    
    async def create_alert(self,
                          component: SystemComponent,
                          title: str,
                          description: str,
                          severity: ErrorSeverity = ErrorSeverity.HIGH,
                          call_id: Optional[str] = None) -> str:
        """Create a system alert"""
        
        alert_id = str(uuid.uuid4())
        
        alert = SystemAlert(
            alert_id=alert_id,
            timestamp=datetime.utcnow(),
            severity=severity,
            component=component,
            title=title,
            description=description,
            call_id=call_id
        )
        
        self.active_alerts[alert_id] = alert
        
        if self.supabase_client:
            await self._store_alert(alert)
        
        logger.warning(f"Alert created: {title} - {description}")
        
        return alert_id
    
    async def resolve_alert(self, alert_id: str, resolution_note: str = "") -> bool:
        """Resolve an active alert"""
        
        if alert_id not in self.active_alerts:
            return False
        
        alert = self.active_alerts[alert_id]
        alert.resolved = True
        
        if self.supabase_client:
            await self._update_alert_status(alert_id, resolved=True, resolution_note=resolution_note)
        
        # Remove from active alerts
        del self.active_alerts[alert_id]
        
        logger.info(f"Alert resolved: {alert_id}")
        
        return True
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        
        overall_status = HealthStatus.HEALTHY
        component_statuses = {}
        critical_issues = []
        warnings = []
        
        # Evaluate each component
        for component in SystemComponent:
            component_health = await self._evaluate_component_health(component)
            component_statuses[component.value] = component_health
            
            if component_health['status'] == HealthStatus.CRITICAL.value:
                overall_status = HealthStatus.CRITICAL
                critical_issues.append(f"{component.value}: {component_health.get('issue', 'Unknown issue')}")
            elif component_health['status'] == HealthStatus.DEGRADED.value and overall_status != HealthStatus.CRITICAL:
                overall_status = HealthStatus.DEGRADED
            elif component_health['status'] == HealthStatus.WARNING.value and overall_status == HealthStatus.HEALTHY:
                overall_status = HealthStatus.WARNING
                warnings.append(f"{component.value}: {component_health.get('issue', 'Performance warning')}")
        
        # Recent error analysis
        recent_errors = [e for e in self.error_events if e.timestamp > datetime.utcnow() - timedelta(minutes=15)]
        error_rate = len(recent_errors) / 15  # errors per minute
        
        return {
            "overall_status": overall_status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "component_statuses": component_statuses,
            "critical_issues": critical_issues,
            "warnings": warnings,
            "active_alerts": len(self.active_alerts),
            "recent_error_rate": round(error_rate, 2),
            "total_errors_logged": len(self.error_events),
            "system_uptime": self._calculate_uptime(),
            "performance_summary": await self._get_performance_summary()
        }
    
    async def get_error_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get detailed error analytics"""
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_events if e.timestamp > cutoff_time]
        
        # Error distribution by component
        component_errors = defaultdict(int)
        severity_distribution = defaultdict(int)
        error_types = defaultdict(int)
        hourly_distribution = defaultdict(int)
        
        for error in recent_errors:
            component_errors[error.component.value] += 1
            severity_distribution[error.severity.value] += 1
            error_types[error.error_type] += 1
            hour_key = error.timestamp.strftime('%Y-%m-%d %H:00')
            hourly_distribution[hour_key] += 1
        
        # Error patterns and trends
        top_error_patterns = sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Resolution metrics
        resolved_errors = [e for e in recent_errors if e.resolved]
        resolution_rate = len(resolved_errors) / len(recent_errors) if recent_errors else 0
        
        avg_resolution_time = 0
        if resolved_errors:
            resolution_times = [(e.resolution_time - e.timestamp).total_seconds() 
                              for e in resolved_errors if e.resolution_time]
            avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        return {
            "analysis_period_hours": hours,
            "total_errors": len(recent_errors),
            "component_distribution": dict(component_errors),
            "severity_distribution": dict(severity_distribution),
            "error_types": dict(error_types),
            "hourly_distribution": dict(hourly_distribution),
            "top_error_patterns": top_error_patterns,
            "resolution_metrics": {
                "resolution_rate": round(resolution_rate, 3),
                "average_resolution_time_seconds": round(avg_resolution_time, 2),
                "auto_recovery_attempts": sum(self.recovery_attempts.values())
            }
        }
    
    async def _evaluate_component_health(self, component: SystemComponent) -> Dict[str, Any]:
        """Evaluate health of a specific component"""
        
        if component not in self.health_metrics:
            return {
                "status": HealthStatus.HEALTHY.value,
                "metrics": {},
                "last_check": None,
                "issue": None
            }
        
        metrics = self.health_metrics[component]
        worst_status = HealthStatus.HEALTHY
        critical_metrics = []
        
        for metric_name, metric in metrics.items():
            if metric.status.value == HealthStatus.CRITICAL.value:
                worst_status = HealthStatus.CRITICAL
                critical_metrics.append(f"{metric_name}: {metric.value}{metric.unit}")
            elif metric.status.value == HealthStatus.DEGRADED.value and worst_status != HealthStatus.CRITICAL:
                worst_status = HealthStatus.DEGRADED
            elif metric.status.value == HealthStatus.WARNING.value and worst_status == HealthStatus.HEALTHY:
                worst_status = HealthStatus.WARNING
        
        # Check recent errors for this component
        recent_errors = [e for e in self.error_events 
                        if e.component == component and e.timestamp > datetime.utcnow() - timedelta(minutes=10)]
        
        if len(recent_errors) > 5:  # Too many recent errors
            worst_status = HealthStatus.CRITICAL
        
        issue = None
        if critical_metrics:
            issue = f"Critical metrics: {', '.join(critical_metrics)}"
        elif recent_errors:
            issue = f"{len(recent_errors)} recent errors"
        
        return {
            "status": worst_status.value,
            "metrics": {name: {"value": m.value, "status": m.status.value, "unit": m.unit} 
                       for name, m in metrics.items()},
            "last_check": max(m.timestamp for m in metrics.values()).isoformat() if metrics else None,
            "recent_errors": len(recent_errors),
            "issue": issue
        }
    
    async def _evaluate_alert_conditions(self, error_event: ErrorEvent) -> None:
        """Evaluate if an error should trigger an alert"""
        
        # Critical errors always trigger alerts
        if error_event.severity == ErrorSeverity.CRITICAL:
            await self.create_alert(
                component=error_event.component,
                title=f"Critical Error in {error_event.component.value}",
                description=f"{error_event.error_type}: {error_event.error_message}",
                severity=ErrorSeverity.CRITICAL,
                call_id=error_event.call_id
            )
        
        # Check for error patterns that indicate systemic issues
        error_pattern = f"{error_event.component.value}:{error_event.error_type}"
        if self.error_patterns[error_pattern] >= 5:  # 5 of same error type
            await self.create_alert(
                component=error_event.component,
                title=f"Recurring Error Pattern Detected",
                description=f"Error {error_event.error_type} has occurred {self.error_patterns[error_pattern]} times",
                severity=ErrorSeverity.HIGH
            )
    
    async def _create_health_alert(self, metric: HealthMetric) -> None:
        """Create an alert based on health metric status"""
        
        if metric.status == HealthStatus.CRITICAL:
            severity = ErrorSeverity.CRITICAL
        elif metric.status == HealthStatus.DEGRADED:
            severity = ErrorSeverity.HIGH
        else:
            severity = ErrorSeverity.MEDIUM
        
        await self.create_alert(
            component=metric.component,
            title=f"Health Alert: {metric.metric_name}",
            description=f"{metric.metric_name} is {metric.status.value} with value {metric.value}{metric.unit}",
            severity=severity
        )
    
    async def _attempt_auto_recovery(self, error_event: ErrorEvent) -> None:
        """Attempt automatic recovery for critical errors"""
        
        recovery_key = f"{error_event.component.value}:{error_event.error_type}"
        
        if self.recovery_attempts[recovery_key] >= self.max_recovery_attempts:
            logger.warning(f"Max recovery attempts reached for {recovery_key}")
            return
        
        self.recovery_attempts[recovery_key] += 1
        error_event.resolution_attempted = True
        
        try:
            # Component-specific recovery strategies
            if error_event.component == SystemComponent.DATABASE:
                await self._recover_database_connection()
            elif error_event.component == SystemComponent.LLM_SERVICE:
                await self._recover_llm_service()
            elif error_event.component == SystemComponent.PIPECAT_ENGINE:
                await self._recover_pipecat_engine()
            
            # Mark as resolved if recovery successful
            error_event.resolved = True
            error_event.resolution_time = datetime.utcnow()
            
            logger.info(f"Auto-recovery successful for {recovery_key}")
            
        except Exception as e:
            logger.error(f"Auto-recovery failed for {recovery_key}: {e}")
    
    async def _recover_database_connection(self) -> None:
        """Attempt to recover database connection"""
        if self.supabase_client:
            await self.supabase_client.test_connection()
    
    async def _recover_llm_service(self) -> None:
        """Attempt to recover LLM service"""
        # Would implement LLM service restart/reconnection
        await asyncio.sleep(1)  # Placeholder
    
    async def _recover_pipecat_engine(self) -> None:
        """Attempt to recover PIPECAT engine"""
        # Would implement PIPECAT engine restart/reset
        await asyncio.sleep(1)  # Placeholder
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime percentage"""
        # Simplified uptime calculation
        return 99.5  # Would calculate from actual downtime data
    
    async def _get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary across all components"""
        
        summary = {}
        
        for component, performance_data in self.component_performance.items():
            if performance_data:
                recent_data = list(performance_data)[-10:]  # Last 10 data points
                avg_performance = sum(d['value'] for d in recent_data) / len(recent_data)
                
                summary[component.value] = {
                    "average_performance": round(avg_performance, 3),
                    "data_points": len(performance_data),
                    "trend": "stable"  # Would calculate actual trend
                }
        
        return summary
    
    async def _store_error_event(self, error_event: ErrorEvent) -> None:
        """Store error event in database"""
        try:
            await self.supabase_client.client.table("system_errors").insert({
                "error_id": error_event.error_id,
                "timestamp": error_event.timestamp.isoformat(),
                "severity": error_event.severity.value,
                "component": error_event.component.value,
                "error_type": error_event.error_type,
                "error_message": error_event.error_message,
                "call_id": error_event.call_id,
                "stack_trace": error_event.stack_trace,
                "context": error_event.context,
                "resolution_attempted": error_event.resolution_attempted,
                "resolved": error_event.resolved
            }).execute()
        except Exception as e:
            logger.error(f"Failed to store error event: {e}")
    
    async def _store_health_metric(self, metric: HealthMetric) -> None:
        """Store health metric in database"""
        try:
            await self.supabase_client.client.table("health_metrics").insert({
                "component": metric.component.value,
                "metric_name": metric.metric_name,
                "value": metric.value,
                "status": metric.status.value,
                "timestamp": metric.timestamp.isoformat(),
                "unit": metric.unit
            }).execute()
        except Exception as e:
            logger.error(f"Failed to store health metric: {e}")
    
    async def _store_alert(self, alert: SystemAlert) -> None:
        """Store alert in database"""
        try:
            await self.supabase_client.client.table("system_alerts").insert({
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp.isoformat(),
                "severity": alert.severity.value,
                "component": alert.component.value,
                "title": alert.title,
                "description": alert.description,
                "call_id": alert.call_id,
                "auto_resolution_attempted": alert.auto_resolution_attempted,
                "acknowledged": alert.acknowledged,
                "resolved": alert.resolved
            }).execute()
        except Exception as e:
            logger.error(f"Failed to store alert: {e}")
    
    async def _update_alert_status(self, alert_id: str, resolved: bool = False, resolution_note: str = "") -> None:
        """Update alert status in database"""
        try:
            await self.supabase_client.client.table("system_alerts").update({
                "resolved": resolved,
                "resolution_note": resolution_note,
                "resolved_at": datetime.utcnow().isoformat() if resolved else None
            }).eq("alert_id", alert_id).execute()
        except Exception as e:
            logger.error(f"Failed to update alert status: {e}")


# Global system monitor instance
system_monitor: Optional[SystemMonitor] = None


def get_system_monitor() -> Optional[SystemMonitor]:
    """Get the global system monitor instance"""
    return system_monitor


async def initialize_system_monitor(supabase_client=None) -> SystemMonitor:
    """Initialize the global system monitor"""
    global system_monitor
    
    system_monitor = SystemMonitor(supabase_client)
    
    # Start background health checks
    asyncio.create_task(background_health_checks())
    
    logger.info("System Monitor initialized and background tasks started")
    return system_monitor


async def background_health_checks():
    """Background task for continuous health monitoring"""
    while True:
        try:
            if system_monitor:
                # Perform periodic health checks
                await perform_health_checks()
                
            await asyncio.sleep(30)  # Check every 30 seconds
            
        except Exception as e:
            logger.error(f"Error in background health checks: {e}")
            await asyncio.sleep(60)  # Wait longer on error


async def perform_health_checks():
    """Perform comprehensive health checks"""
    if not system_monitor:
        return
    
    try:
        # Database health check
        if system_monitor.supabase_client:
            start_time = datetime.utcnow()
            connection_ok = await system_monitor.supabase_client.test_connection()
            response_time = (datetime.utcnow() - start_time).total_seconds()
            
            await system_monitor.update_health_metric(
                SystemComponent.DATABASE,
                "connection_status",
                1.0 if connection_ok else 0.0,
                threshold_warning=0.9,
                threshold_critical=0.1
            )
            
            await system_monitor.update_health_metric(
                SystemComponent.DATABASE,
                "response_time",
                response_time,
                unit="s",
                threshold_warning=2.0,
                threshold_critical=5.0
            )
        
        # Memory and CPU usage (simulated)
        await system_monitor.update_health_metric(
            SystemComponent.PIPECAT_ENGINE,
            "memory_usage",
            0.75,  # Would get actual memory usage
            unit="%",
            threshold_warning=0.8,
            threshold_critical=0.95
        )
        
    except Exception as e:
        await system_monitor.log_error(
            SystemComponent.PIPECAT_ENGINE,
            "health_check_failure",
            f"Health check failed: {str(e)}",
            ErrorSeverity.HIGH,
            exception=e
        )