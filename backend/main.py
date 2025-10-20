import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.database.supabase import supabase_client
from app.routes import agent_routes, call_routes, webhook_routes, analytics_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    connection_success = await supabase_client.test_connection()
    
    try:
        from app.pipecat.pipecat_service import pipecat_service
        pipecat_initialized = await pipecat_service.initialize(
            openai_api_key=settings.openai_api_key,
            cartesia_api_key=getattr(settings, 'cartesia_api_key', None),
            deepgram_api_key=getattr(settings, 'deepgram_api_key', None)
        )
    except Exception as e:
        pass
    
    yield  
    
    try:
        from app.pipecat.pipecat_service import pipecat_service
        await pipecat_service.shutdown()
    except Exception as e:
        pass
    

app = FastAPI(
    title=settings.app_title,
    version=settings.app_version,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_routes.router)
app.include_router(call_routes.router)
app.include_router(webhook_routes.router)
app.include_router(analytics_routes.router)

@app.get("/")
async def read_root():
    """Root endpoint with API information"""
    return {
        "message": "Voice Agent API is running!",
        "version": settings.app_version,
    }

@app.post("/")
async def post_root(request: Request):
    """Handle POST requests to root (webhooks, health checks, etc.)"""
    return {
        "message": "POST received at root endpoint",
        "status": "ok",
        "version": settings.app_version,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.reload,
        log_level="info"  
    )