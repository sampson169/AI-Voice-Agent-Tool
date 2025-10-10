from fastapi import APIRouter, HTTPException
from app.models.schemas import AgentConfigCreate, AgentConfigResponse
from app.database.supabase import supabase_client
from app.services.retell_service import retell_service
from typing import List
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.post("/", response_model=AgentConfigResponse)
async def create_agent_config(config: AgentConfigCreate):
    try:
        config_data = {
            "id": str(uuid.uuid4()),
            "name": config.name,
            "prompt": config.prompt,
            "voice_settings": config.voice_settings,
            "emergency_phrases": config.emergency_phrases,
            "structured_fields": config.structured_fields,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        retell_agent = await retell_service.create_agent(config_data)
        if retell_agent:
            config_data["retell_agent_id"] = retell_agent.get("agent_id")
        
        result = await supabase_client.create_agent_config(config_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create agent configuration")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@router.get("/", response_model=list[AgentConfigResponse])
async def get_all_agent_configs():
    try:
        configs = await supabase_client.get_all_agent_configs()
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agents: {str(e)}")

@router.get("/{config_id}", response_model=AgentConfigResponse)
async def get_agent_config(config_id: str):
    try:
        config = await supabase_client.get_agent_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Agent configuration not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent: {str(e)}")

@router.put("/{config_id}", response_model=AgentConfigResponse)
async def update_agent_config(config_id: str, updates: AgentConfigCreate):
    try:
        update_data = {
            "name": updates.name,
            "prompt": updates.prompt,
            "voice_settings": updates.voice_settings,
            "emergency_phrases": updates.emergency_phrases,
            "structured_fields": updates.structured_fields,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = await supabase_client.update_agent_config(config_id, update_data)
        
        if not result:
            raise HTTPException(status_code=404, detail="Agent configuration not found")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating agent: {str(e)}")

@router.post("/", response_model=AgentConfigResponse)
async def create_agent_config(config: AgentConfigCreate):
    """Create a new agent configuration"""
    try:
        config_data = config.dict()
        result = await supabase_client.create_agent_config(config_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create agent configuration")
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent config: {str(e)}")

@router.get("/", response_model=List[AgentConfigResponse])
async def get_all_agent_configs():
    """Get all agent configurations"""
    try:
        configs = await supabase_client.get_all_agent_configs()
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent configs: {str(e)}")

@router.get("/{config_id}", response_model=AgentConfigResponse)
async def get_agent_config(config_id: str):
    """Get agent configuration by ID"""
    try:
        config = await supabase_client.get_agent_config(config_id)
        
        if not config:
            raise HTTPException(status_code=404, detail="Agent configuration not found")
        
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent config: {str(e)}")

@router.put("/{config_id}", response_model=AgentConfigResponse)
async def update_agent_config(config_id: str, config: AgentConfigCreate):
    """Update agent configuration"""
    try:
        updates = config.dict()
        result = await supabase_client.update_agent_config(config_id, updates)
        
        if not result:
            raise HTTPException(status_code=404, detail="Agent configuration not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating agent config: {str(e)}")