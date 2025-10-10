import re
from typing import Dict, Any, Tuple
from models.schemas import CallSummary, CallOutcome, DriverStatus, EmergencyType

class CallProcessingService:
    def __init__(self):
        self.emergency_phrases = [
            "emergency", "accident", "breakdown", "medical", "help", "urgent",
            "blowout", "flat tire", "crash", "injured", "stranded"
        ]
        
        self.location_patterns = [
            r"(I|US|State Route|SR|Highway|HWY|Route)\s*(\d+)",
            r"mile\s*marker\s*(\d+)",
            r"near\s+([A-Za-z\s]+)",
            r"([A-Za-z\s]+)\s+exit"
        ]
        
        self.time_patterns = [
            r"(\d+:\d+\s*(AM|PM))",
            r"(tomorrow|today|this\s+afternoon|this\s+evening|tonight)",
            r"in\s+(\d+)\s+(hour|minute)s?"
        ]

    def process_transcript(self, transcript: str, emergency_phrases: list = None) -> CallSummary:
        """Process transcript and extract structured data"""
        if emergency_phrases:
            self.emergency_phrases.extend(emergency_phrases)
        
        transcript_lower = transcript.lower()
        
        # Check for emergency first
        if self._is_emergency(transcript_lower):
            return self._process_emergency(transcript)
        
        # Process normal call
        return self._process_normal_call(transcript)

    def _is_emergency(self, transcript: str) -> bool:
        """Check if transcript contains emergency phrases"""
        return any(phrase in transcript for phrase in self.emergency_phrases)

    def _process_emergency(self, transcript: str) -> CallSummary:
        """Process emergency scenario"""
        summary = CallSummary(
            call_outcome="Emergency Escalation",
            escalation_status="Connected to Human Dispatcher"
        )
        
        # Extract emergency type
        if "accident" in transcript.lower() or "crash" in transcript.lower():
            summary.emergency_type = "Accident"
        elif "breakdown" in transcript.lower() or "blowout" in transcript.lower():
            summary.emergency_type = "Breakdown"
        elif "medical" in transcript.lower() or "injured" in transcript.lower():
            summary.emergency_type = "Medical"
        else:
            summary.emergency_type = "Other"
        
        # Extract safety information
        if "safe" in transcript.lower() or "ok" in transcript.lower():
            summary.safety_status = "Driver confirmed everyone is safe"
        if "injured" not in transcript.lower() or "no injury" in transcript.lower():
            summary.injury_status = "No injuries reported"
        
        # Extract location
        summary.emergency_location = self._extract_location(transcript)
        
        # Check load security
        if "secure" in transcript.lower() or "fine" in transcript.lower():
            summary.load_secure = True
        
        return summary

    def _process_normal_call(self, transcript: str) -> CallSummary:
        """Process normal check-in call"""
        summary = CallSummary()
        
        # Determine call outcome
        if any(word in transcript.lower() for word in ["arrived", "delivered", "at destination"]):
            summary.call_outcome = "Arrival Confirmation"
            summary.driver_status = "Arrived"
        else:
            summary.call_outcome = "In-Transit Update"
            if any(word in transcript.lower() for word in ["delay", "late", "traffic", "waiting"]):
                summary.driver_status = "Delayed"
            elif any(word in transcript.lower() for word in ["unload", "unloading", "dock"]):
                summary.driver_status = "Unloading"
            else:
                summary.driver_status = "Driving"
        
        # Extract location
        summary.current_location = self._extract_location(transcript)
        
        # Extract ETA
        summary.eta = self._extract_eta(transcript)
        
        # Extract delay reason
        summary.delay_reason = self._extract_delay_reason(transcript)
        
        # Extract unloading status
        summary.unloading_status = self._extract_unloading_status(transcript)
        
        # Check POD reminder
        summary.pod_reminder_acknowledged = "pod" in transcript.lower() or "proof" in transcript.lower()
        
        return summary

    def _extract_location(self, transcript: str) -> str:
        """Extract location information from transcript"""
        for pattern in self.location_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            if matches:
                return matches[0] if isinstance(matches[0], str) else " ".join(matches[0])
        return "Location not specified"

    def _extract_eta(self, transcript: str) -> str:
        """Extract ETA from transcript"""
        for pattern in self.time_patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            if matches:
                return matches[0][0] if isinstance(matches[0], tuple) else matches[0]
        return "ETA not specified"

    def _extract_delay_reason(self, transcript: str) -> str:
        """Extract delay reason from transcript"""
        delay_keywords = {
            "traffic": "Heavy Traffic",
            "weather": "Weather",
            "mechanical": "Mechanical Issues",
            "loading": "Loading/Unloading Delay",
            "break": "Break",
            "scale": "Scale Inspection"
        }
        
        for keyword, reason in delay_keywords.items():
            if keyword in transcript.lower():
                return reason
        return "None"

    def _extract_unloading_status(self, transcript: str) -> str:
        """Extract unloading status from transcript"""
        if "unloading" in transcript.lower():
            if "door" in transcript.lower():
                return "In Door"
            elif "lumper" in transcript.lower():
                return "Waiting for Lumper"
            elif "detention" in transcript.lower():
                return "Detention"
            else:
                return "Unloading"
        return "N/A"

# Initialize call processing service
call_processor = CallProcessingService()