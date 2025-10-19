"""
Data models for PIPECAT Voice Agent
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class ScenarioType(str, Enum):
    """Types of conversation scenarios"""
    GENERAL = "general"
    DRIVER_CHECKIN = "driver_checkin"
    EMERGENCY_PROTOCOL = "emergency_protocol"


class ConversationPhase(str, Enum):
    """Phases of conversation flow"""
    GREETING = "greeting"
    STATUS_INQUIRY = "status_inquiry"
    LOCATION_ETA = "location_eta"
    ARRIVAL_DETAILS = "arrival_details"
    DELAY_DETAILS = "delay_details"
    CLARIFICATION = "clarification"
    EMERGENCY = "emergency"
    WRAP_UP = "wrap_up"


class CallOutcome(str, Enum):
    """Possible call outcomes"""
    IN_TRANSIT_UPDATE = "In-Transit Update"
    ARRIVAL_CONFIRMATION = "Arrival Confirmation"
    EMERGENCY_ESCALATION = "Emergency Escalation"


class DriverStatus(str, Enum):
    """Driver status options"""
    DRIVING = "Driving"
    DELAYED = "Delayed"
    ARRIVED = "Arrived"
    UNLOADING = "Unloading"


class EmergencyType(str, Enum):
    """Types of emergencies"""
    ACCIDENT = "Accident"
    BREAKDOWN = "Breakdown"
    MEDICAL = "Medical"
    OTHER = "Other"


class CallContext(BaseModel):
    """Context information for a voice call"""
    call_id: str
    driver_name: str
    load_number: str
    phone_number: Optional[str] = None
    agent_id: str = "default-logistics-agent"
    scenario_type: ScenarioType = ScenarioType.GENERAL
    call_type: str = "web"  # "web" or "phone"
    
    class Config:
        use_enum_values = True


class ConversationState(BaseModel):
    """Current state of the conversation"""
    phase: ConversationPhase = ConversationPhase.GREETING
    emergency_detected: bool = False
    clarification_attempts: int = 0
    scenario_type: ScenarioType = ScenarioType.GENERAL
    tokens_used: int = 0
    interruption_count: int = 0
    sentiment_shifts: List[Dict[str, Any]] = []
    last_utterance: str = ""  # Store the last user utterance
    
    class Config:
        use_enum_values = True


class StructuredData(BaseModel):
    """Structured data extracted from conversation"""
    call_outcome: Optional[CallOutcome] = None
    driver_status: Optional[DriverStatus] = None
    current_location: Optional[str] = None
    eta: Optional[str] = None
    delay_reason: Optional[str] = "None"
    unloading_status: Optional[str] = "N/A"
    pod_reminder_acknowledged: bool = False
    
    # Emergency-specific fields
    emergency_type: Optional[EmergencyType] = None
    safety_status: Optional[str] = None
    injury_status: Optional[str] = None
    emergency_location: Optional[str] = None
    load_secure: Optional[bool] = None
    escalation_status: Optional[str] = None
    
    class Config:
        use_enum_values = True


class RTVIEvent(BaseModel):
    """Real-Time Voice Interaction event"""
    event_id: str
    call_id: str
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class CallMetrics(BaseModel):
    """Metrics for a voice call"""
    call_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    total_tokens: int = 0
    interruption_count: int = 0
    sentiment_shifts: int = 0
    final_outcome: Optional[CallOutcome] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        use_enum_values = True


class AnalyticsAggregation(BaseModel):
    """Aggregated analytics data"""
    total_calls: int = 0
    avg_call_duration: float = 0.0
    total_interruptions: int = 0
    emergency_calls: int = 0
    successful_calls: int = 0
    total_tokens_spent: int = 0
    avg_tokens_per_call: float = 0.0
    
    # Outcome distribution
    in_transit_updates: int = 0
    arrival_confirmations: int = 0
    emergency_escalations: int = 0
    
    # Time period
    start_date: datetime
    end_date: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }