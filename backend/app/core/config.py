from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Voice Agent Tool"
    app_version: str = "1.0.0"
    debug: bool = False
    
    host: str = "localhost"
    port: int = 8000
    reload: bool = True
    log_level: str = "INFO"
    
    allowed_origins: str = "http://localhost:3000,http://localhost:5173"
    
    supabase_url: str = Field()
    supabase_key: str = Field()
    retell_api_key: str = Field()
    retell_base_url: str = "https://api.retellai.com/v2"
    retell_agent_id: Optional[str] = None
    retell_webhook_url: Optional[str] = None

    @property
    def origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()