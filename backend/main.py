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
    
    # Initialize monitoring integration
    try:
        from app.pipecat.monitoring_integration import initialize_monitoring
        await initialize_monitoring()
    except Exception as e:
        print(f"Warning: Failed to initialize monitoring: {e}")
    
    # Initialize smart call routing
    try:
        from app.pipecat.smart_call_router import initialize_smart_router
        await initialize_smart_router()
    except Exception as e:
        print(f"Warning: Failed to initialize smart router: {e}")
    
    # Initialize conversation analyzer
    try:
        from app.pipecat.conversation_analyzer import initialize_conversation_analyzer
        await initialize_conversation_analyzer()
    except Exception as e:
        print(f"Warning: Failed to initialize conversation analyzer: {e}")
    
    # Initialize sentiment analyzer
    try:
        from app.pipecat.driver_sentiment_analyzer import initialize_sentiment_analyzer
        await initialize_sentiment_analyzer()
    except Exception as e:
        print(f"Warning: Failed to initialize sentiment analyzer: {e}")
    
    yield  
    
    # Shutdown monitoring
    try:
        from app.pipecat.monitoring_integration import shutdown_monitoring
        await shutdown_monitoring()
    except Exception as e:
        pass
    
    # Note: Smart router, conversation analyzer, and sentiment analyzer
    # don't require explicit shutdown as they're stateless services
    
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