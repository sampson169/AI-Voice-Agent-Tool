from fastapi import APIRouter, HTTPException
from app.models.schemas import AgentConfigCreate, AgentConfigResponse
from app.database.supabase import supabase_client
from app.services.retell_service import retell_service
from app.services.prompt_templates import LogisticsPromptTemplates
from typing import List, Dict, Any
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.post("/", response_model=AgentConfigResponse)
async def create_agent_config(config: AgentConfigCreate):
    """Create a new agent configuration"""
    try:
        config_data = {
            "id": str(uuid.uuid4()),
            "name": config.name,
            "prompt": config.prompt,
            "scenario_type": getattr(config, 'scenario_type', 'general'),
            "voice_settings": config.voice_settings,
            "emergency_phrases": config.emergency_phrases,
            "structured_fields": config.structured_fields,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            retell_agent = await retell_service.create_agent(config_data)
            if retell_agent:
                config_data["retell_agent_id"] = retell_agent.get("agent_id")
        except Exception as e:
            pass
        
        result = await supabase_client.create_agent_config(config_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create agent configuration")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")

@router.get("/", response_model=List[AgentConfigResponse])
async def get_all_agent_configs():
    """Get all agent configurations"""
    try:
        configs = await supabase_client.get_all_agent_configs()
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agents: {str(e)}")

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
        raise HTTPException(status_code=500, detail=f"Error fetching agent: {str(e)}")

@router.put("/{config_id}", response_model=AgentConfigResponse)
async def update_agent_config(config_id: str, updates: AgentConfigCreate):
    """Update agent configuration"""
    try:
        update_data = {
            "name": updates.name,
            "prompt": updates.prompt,
            "scenario_type": getattr(updates, 'scenario_type', 'general'),
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

@router.get("/templates/scenarios")
async def get_scenario_templates():
    """Get available scenario templates"""
    try:
        templates = {
            "driver_checkin": LogisticsPromptTemplates.get_scenario_template("driver_checkin"),
            "emergency_protocol": LogisticsPromptTemplates.get_scenario_template("emergency_protocol"),
            "general": LogisticsPromptTemplates.get_scenario_template("general")
        }
        return {"templates": templates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

@router.post("/templates/{scenario_type}")
async def create_agent_from_template(scenario_type: str, custom_name: str = None) -> Dict[str, Any]:
    """Create an agent configuration from a predefined template"""
    try:
        template = LogisticsPromptTemplates.get_scenario_template(scenario_type)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template not found: {scenario_type}")
        
        config_data = {
            "id": str(uuid.uuid4()),
            "name": custom_name or template["name"],
            "prompt": template["prompt"],
            "scenario_type": scenario_type,
            "voice_settings": template["voice_settings"],
            "emergency_phrases": template["emergency_phrases"],
            "structured_fields": template["structured_fields"],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        try:
            retell_agent = await retell_service.create_agent(config_data)
            if retell_agent:
                config_data["retell_agent_id"] = retell_agent.get("agent_id")
        except Exception as e:
            pass
        
        result = await supabase_client.create_agent_config(config_data)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create agent from template")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent from template: {str(e)}")