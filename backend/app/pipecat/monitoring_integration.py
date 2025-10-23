from typing import Optional, Dict, Any
import asyncio
import logging
from datetime import datetime, timedelta
from .system_monitor import SystemMonitor, get_system_monitor
from .rtvi_analytics import get_analytics_observer
from .voice_quality_assessor import VoiceQualityAssessor


logger = logging.getLogger(__name__)


class MonitoringIntegration:
    """
    Integration layer connecting system monitoring with RTVI analytics and voice quality assessment
    """
    
    def __init__(self):
        self.system_monitor: Optional[SystemMonitor] = None
        self.analytics_observer = None
        self.voice_assessor: Optional[VoiceQualityAssessor] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
    
    async def initialize(self):
        """Initialize all monitoring components"""
        try:
            # Initialize system monitor
            self.system_monitor = get_system_monitor()
            if self.system_monitor:
                await self.system_monitor.start()
                logger.info("System monitor initialized")
            
            # Initialize analytics observer
            self.analytics_observer = get_analytics_observer()
            if self.analytics_observer:
                logger.info("Analytics observer connected")
            
            # Initialize voice quality assessor
            self.voice_assessor = VoiceQualityAssessor()
            logger.info("Voice quality assessor initialized")
            
            # Start monitoring loop
            self.is_running = True
            self.monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("Monitoring integration fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring integration: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown all monitoring components"""
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.system_monitor:
            await self.system_monitor.stop()
        
        logger.info("Monitoring integration shutdown complete")
    
    async def _monitoring_loop(self):
        """Main monitoring loop for cross-component analysis"""
        while self.is_running:
            try:
                await self._perform_health_checks()
                await self._analyze_trends()
                await self._check_alerts()
                
                # Wait 30 seconds between monitoring cycles
                await asyncio.sleep(30)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(10)  # Short delay before retry
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks across all components"""
        if not self.system_monitor:
            return
        
        # Check system resources
        health_status = await self.system_monitor.get_system_health()
        
        # Check for concerning patterns
        if health_status.get("overall_status") == "critical":
            await self.system_monitor.create_alert(
                severity="critical",
                component="system",
                title="System Health Critical",
                description="System health has degraded to critical status"
            )
    
    async def _analyze_trends(self):
        """Analyze trends across monitoring data"""
        if not self.system_monitor:
            return
        
        try:
            # Get recent error patterns
            error_analytics = await self.system_monitor.get_error_analytics(hours=1)
            
            # Check for error spikes
            recent_errors = error_analytics.get("total_errors", 0)
            if recent_errors > 10:  # Threshold for concern
                await self.system_monitor.create_alert(
                    severity="warning",
                    component="error_tracking",
                    title="Error Spike Detected",
                    description=f"Detected {recent_errors} errors in the last hour"
                )
            
            # Analyze quality trends if voice assessor is available
            if self.voice_assessor:
                await self._analyze_quality_trends()
                
        except Exception as e:
            logger.error(f"Error analyzing trends: {e}")
    
    async def _analyze_quality_trends(self):
        """Analyze voice quality trends"""
        # This would typically analyze recent call quality data
        # For now, we'll simulate quality trend analysis
        pass
    
    async def _check_alerts(self):
        """Check and process active alerts"""
        if not self.system_monitor:
            return
        
        active_alerts = list(self.system_monitor.active_alerts.values())
        
        # Auto-resolve old alerts (older than 1 hour)
        current_time = datetime.utcnow()
        for alert in active_alerts:
            if (current_time - alert.timestamp) > timedelta(hours=1):
                if alert.severity.value in ["info", "warning"]:
                    await self.system_monitor.resolve_alert(
                        alert.alert_id, 
                        "Auto-resolved: Alert aged out"
                    )
    
    async def handle_call_start(self, call_id: str, call_metadata: Dict[str, Any]):
        """Handle the start of a new call"""
        try:
            if self.system_monitor:
                await self.system_monitor.track_event(
                    event_type="call_started",
                    severity="info",
                    component="pipecat_engine",
                    message=f"Call {call_id} started",
                    call_id=call_id,
                    metadata=call_metadata
                )
            
            logger.info(f"Monitoring started for call {call_id}")
            
        except Exception as e:
            logger.error(f"Error handling call start monitoring: {e}")
    
    async def handle_call_end(self, call_id: str, call_summary: Dict[str, Any]):
        """Handle the end of a call with quality assessment"""
        try:
            if self.system_monitor:
                await self.system_monitor.track_event(
                    event_type="call_completed",
                    severity="info",
                    component="pipecat_engine",
                    message=f"Call {call_id} completed",
                    call_id=call_id,
                    metadata=call_summary
                )
            
            # Trigger voice quality assessment if available
            if self.voice_assessor and call_summary.get("audio_file_path"):
                quality_result = await self.voice_assessor.assess_call_quality(
                    call_id, call_summary
                )
                
                # Create alert if quality is concerning
                if quality_result.get("overall_score", 0) < 0.6:
                    await self.system_monitor.create_alert(
                        severity="warning",
                        component="voice_quality",
                        title="Low Call Quality Detected",
                        description=f"Call {call_id} had quality score {quality_result.get('overall_score', 0):.2f}",
                        call_id=call_id
                    )
            
            logger.info(f"Monitoring completed for call {call_id}")
            
        except Exception as e:
            logger.error(f"Error handling call end monitoring: {e}")
    
    async def handle_error(self, error_context: Dict[str, Any]):
        """Handle error events across the system"""
        try:
            if self.system_monitor:
                await self.system_monitor.track_event(
                    event_type="error_occurred",
                    severity=error_context.get("severity", "error"),
                    component=error_context.get("component", "unknown"),
                    message=error_context.get("message", "Unspecified error"),
                    call_id=error_context.get("call_id"),
                    metadata=error_context
                )
            
            # Create alert for critical errors
            if error_context.get("severity") == "critical":
                await self.system_monitor.create_alert(
                    severity="critical",
                    component=error_context.get("component", "unknown"),
                    title="Critical Error Detected",
                    description=error_context.get("message", "Critical error occurred"),
                    call_id=error_context.get("call_id")
                )
            
        except Exception as e:
            logger.error(f"Error handling error event: {e}")
    
    async def get_monitoring_status(self) -> Dict[str, Any]:
        """Get comprehensive monitoring status"""
        try:
            status = {
                "integration_status": "running" if self.is_running else "stopped",
                "components": {
                    "system_monitor": "active" if self.system_monitor else "inactive",
                    "analytics_observer": "active" if self.analytics_observer else "inactive",
                    "voice_assessor": "active" if self.voice_assessor else "inactive"
                },
                "monitoring_loop": "running" if self.monitoring_task and not self.monitoring_task.done() else "stopped"
            }
            
            if self.system_monitor:
                health_data = await self.system_monitor.get_system_health()
                status["system_health"] = health_data
                status["active_alerts"] = len(self.system_monitor.active_alerts)
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting monitoring status: {e}")
            return {"error": str(e)}


# Global monitoring integration instance
_monitoring_integration: Optional[MonitoringIntegration] = None


def get_monitoring_integration() -> Optional[MonitoringIntegration]:
    """Get the global monitoring integration instance"""
    global _monitoring_integration
    return _monitoring_integration


async def initialize_monitoring():
    """Initialize the global monitoring integration"""
    global _monitoring_integration
    
    if _monitoring_integration is None:
        _monitoring_integration = MonitoringIntegration()
        await _monitoring_integration.initialize()
        logger.info("Global monitoring integration initialized")
    
    return _monitoring_integration


async def shutdown_monitoring():
    """Shutdown the global monitoring integration"""
    global _monitoring_integration
    
    if _monitoring_integration:
        await _monitoring_integration.shutdown()
        _monitoring_integration = None
        logger.info("Global monitoring integration shutdown")