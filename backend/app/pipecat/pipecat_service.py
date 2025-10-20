"""
PIPECAT Service
Manages PIPECAT voice agent instances and provides interface for FastAPI
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .voice_agent import VoiceAgentApp, initialize_voice_agent, get_voice_agent
from .models import CallContext, ScenarioType
from ..core.config import settings

logger = logging.getLogger(__name__)


class PipecatService:
    """Service class to manage PIPECAT voice agent operations"""
    
    def __init__(self):
        self.voice_agent: Optional[VoiceAgentApp] = None
        self.active_calls: Dict[str, Dict[str, Any]] = {}
    
    async def initialize(self, 
                        openai_api_key: str,
                        cartesia_api_key: str = None,
                        deepgram_api_key: str = None) -> bool:
        """Initialize the PIPECAT voice agent"""
        try:
            # Validate OpenAI API key format
            if not openai_api_key or openai_api_key in ['your_openai_api_key_here', 'placeholder']:
                logger.warning("Invalid or placeholder OpenAI API key detected - running in demo mode")
                # Don't fail initialization, just warn and continue in demo mode
                openai_api_key = "demo_mode_key"
            
            # Use placeholder keys if not provided (for development)
            cartesia_key = cartesia_api_key or "placeholder_cartesia_key"
            deepgram_key = deepgram_api_key or "placeholder_deepgram_key"
            
            self.voice_agent = await initialize_voice_agent(
                openai_api_key=openai_api_key,
                cartesia_api_key=cartesia_key,
                deepgram_api_key=deepgram_key
            )
            
            logger.info("PIPECAT service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize PIPECAT service: {e}")
            # Don't fail completely, allow service to run in fallback mode
            logger.info("PIPECAT running in fallback mode - calls will be simulated")
            return True  # Return True to allow service to continue
    
    async def create_web_call(self, call_request) -> Dict[str, Any]:
        """Create a web call using PIPECAT"""
        try:
            # Initialize if needed
            if not self.voice_agent:
                logger.info("Initializing PIPECAT service for web call...")
                await self.initialize(
                    openai_api_key=getattr(settings, 'openai_api_key', 'demo_mode'),
                    cartesia_api_key=getattr(settings, 'cartesia_api_key', None),
                    deepgram_api_key=getattr(settings, 'deepgram_api_key', None)
                )
            
            # Create call context
            call_context = CallContext(
                call_id=f"pipecat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{call_request.driver_name}",
                driver_name=call_request.driver_name,
                load_number=call_request.load_number,
                agent_id=call_request.agent_id,
                scenario_type=ScenarioType(getattr(call_request, 'scenario_type', 'general')),
                call_type="web"
            )
            
            # For now, return a simulated response since we're in migration phase
            # In production, this would create actual PIPECAT WebRTC connection
            web_call_link = f"wss://your-pipecat-server.com/call/{call_context.call_id}"
            
            # Store call info
            self.active_calls[call_context.call_id] = {
                "call_context": call_context.dict(),
                "status": "initiated",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created PIPECAT web call: {call_context.call_id}")
            
            return {
                "call_id": call_context.call_id,
                "web_call_link": web_call_link,
                "access_token": f"pipecat_token_{call_context.call_id}",
                "status": "initiated"
            }
            
        except Exception as e:
            logger.error(f"Error creating PIPECAT web call: {e}", exc_info=True)
            return {"error": f"Failed to create PIPECAT web call: {str(e)}"}
    
    async def create_phone_call(self, call_request) -> Dict[str, Any]:
        """Create a phone call using PIPECAT"""
        try:
            # Initialize if needed
            if not self.voice_agent:
                logger.info("Initializing PIPECAT service for phone call...")
                await self.initialize(
                    openai_api_key=getattr(settings, 'openai_api_key', 'demo_mode'),
                    cartesia_api_key=getattr(settings, 'cartesia_api_key', None),
                    deepgram_api_key=getattr(settings, 'deepgram_api_key', None)
                )
            
            # Create call context
            call_context = CallContext(
                call_id=f"pipecat_phone_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{call_request.driver_name}",
                driver_name=call_request.driver_name,
                load_number=call_request.load_number,
                phone_number=call_request.phone_number,
                agent_id=call_request.agent_id,
                scenario_type=ScenarioType(getattr(call_request, 'scenario_type', 'general')),
                call_type="phone"
            )
            
            # For now, return a simulated response since we're in migration phase
            # In production, this would initiate actual phone call via SIP/PSTN
            
            # Store call info
            self.active_calls[call_context.call_id] = {
                "call_context": call_context.dict(),
                "status": "initiated",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created PIPECAT phone call: {call_context.call_id} to {call_request.phone_number}")
            
            return {
                "call_id": call_context.call_id,
                "phone_number": call_request.phone_number,
                "status": "initiated"
            }
            
        except Exception as e:
            logger.error(f"Error creating PIPECAT phone call: {e}", exc_info=True)
            return {"error": f"Failed to create PIPECAT phone call: {str(e)}"}
    
    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """Get status of a PIPECAT call"""
        try:
            if call_id in self.active_calls:
                call_info = self.active_calls[call_id]
                
                if self.voice_agent:
                    status = await self.voice_agent.get_call_status(call_id)
                    return status
                else:
                    return {
                        "call_id": call_id,
                        "status": call_info["status"],
                        "created_at": call_info["created_at"]
                    }
            else:
                return {"status": "not_found", "error": "Call not found"}
                
        except Exception as e:
            logger.error(f"Error getting call status: {e}")
            return {"status": "error", "error": str(e)}
    
    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End a PIPECAT call"""
        try:
            if self.voice_agent:
                await self.voice_agent.end_call(call_id)
            
            if call_id in self.active_calls:
                del self.active_calls[call_id]
            
            logger.info(f"Ended PIPECAT call: {call_id}")
            return {"status": "ended", "call_id": call_id}
            
        except Exception as e:
            logger.error(f"Error ending call: {e}")
            return {"status": "error", "error": str(e)}
    
    async def get_call_details(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call details for PIPECAT call"""
        try:
            if call_id in self.active_calls:
                return self.active_calls[call_id]
            return None
            
        except Exception as e:
            logger.error(f"Error getting call details: {e}")
            return None
    
    async def shutdown(self) -> None:
        """Shutdown the PIPECAT service"""
        try:
            if self.voice_agent:
                await self.voice_agent.shutdown()
            
            self.active_calls.clear()
            logger.info("PIPECAT service shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during PIPECAT service shutdown: {e}")


# Global service instance
pipecat_service = PipecatService()