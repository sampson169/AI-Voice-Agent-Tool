from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class CallType(str, Enum):
    PHONE = "phone"
    WEB = "web"

class CallOutcome(str, Enum):
    IN_TRANSIT_UPDATE = "In-Transit Update"
    ARRIVAL_CONFIRMATION = "Arrival Confirmation"
    EMERGENCY_ESCALATION = "Emergency Escalation"

class DriverStatus(str, Enum):
    DRIVING = "Driving"
    DELAYED = "Delayed"
    ARRIVED = "Arrived"
    UNLOADING = "Unloading"

class EmergencyType(str, Enum):
    ACCIDENT = "Accident"
    BREAKDOWN = "Breakdown"
    MEDICAL = "Medical"
    OTHER = "Other"

# Request Models
class AgentConfigCreate(BaseModel):
    name: str = Field(..., description="Name of the agent configuration")
    prompt: str = Field(..., description="Main conversation prompt")
    scenario_type: str = Field(default="general", description="Type of logistics scenario")
    voice_settings: Dict[str, Any] = Field(default_factory=dict)
    emergency_phrases: List[str] = Field(default_factory=list)
    structured_fields: List[Dict[str, Any]] = Field(default_factory=list)
    retell_agent_id: Optional[str] = Field(None, description="Associated Retell agent ID")

class CallRequest(BaseModel):
    driver_name: str = Field(..., description="Name of the driver")
    phone_number: Optional[str] = Field(None, description="Phone number for phone calls")
    load_number: str = Field(..., description="Load number for context")
    agent_id: str = Field(..., description="Retell agent ID")
    call_type: CallType = Field(..., description="Type of call")

class RetellWebhook(BaseModel):
    call_id: str = Field(..., description="Retell call ID")
    transcript: str = Field(..., description="Full conversation transcript")
    current_utterance: str = Field(..., description="Latest utterance from user")
    timestamp: str = Field(..., description="Event timestamp")

# Response Models
class CallSummary(BaseModel):
    call_outcome: Optional[CallOutcome] = None
    driver_status: Optional[DriverStatus] = None
    current_location: Optional[str] = None
    eta: Optional[str] = None
    delay_reason: Optional[str] = None
    unloading_status: Optional[str] = None
    pod_reminder_acknowledged: Optional[bool] = None
    emergency_type: Optional[EmergencyType] = None
    safety_status: Optional[str] = None
    injury_status: Optional[str] = None
    emergency_location: Optional[str] = None
    load_secure: Optional[bool] = None
    escalation_status: Optional[str] = None

class CallResult(BaseModel):
    id: str
    call_request: CallRequest
    transcript: str
    summary: CallSummary
    timestamp: datetime
    duration: int
    retell_call_id: Optional[str] = None

class AgentConfigResponse(BaseModel):
    id: str
    name: str
    prompt: str
    scenario_type: str
    voice_settings: Dict[str, Any]
    emergency_phrases: List[str]
    structured_fields: List[Dict[str, Any]]
    retell_agent_id: Optional[str]
    created_at: datetime
    updated_at: datetime