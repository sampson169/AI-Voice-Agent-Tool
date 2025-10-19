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
    print("🚀 Starting Voice Agent Tool...")
    
    # Test Supabase connection
    connection_success = await supabase_client.test_connection()
    if connection_success:
        print("✅ Supabase connected successfully!")
    else:
        print("❌ Supabase connection failed - check your configuration")
    
    # Initialize PIPECAT service
    try:
        from app.pipecat.pipecat_service import pipecat_service
        pipecat_initialized = await pipecat_service.initialize(
            openai_api_key=settings.openai_api_key,
            cartesia_api_key=getattr(settings, 'cartesia_api_key', None),
            deepgram_api_key=getattr(settings, 'deepgram_api_key', None)
        )
        
        if pipecat_initialized:
            print("✅ PIPECAT voice agent initialized successfully!")
        else:
            print("⚠️ PIPECAT initialization failed - using fallback mode")
    except Exception as e:
        print(f"⚠️ PIPECAT initialization error: {e} - using fallback mode")
    
    yield  
    
    # Cleanup
    print("👋 Shutting down Voice Agent Tool...")
    try:
        from app.pipecat.pipecat_service import pipecat_service
        await pipecat_service.shutdown()
    except Exception as e:
        print(f"Warning: Error during PIPECAT shutdown: {e}")
    

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
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    print(f"🔔 POST request to root from {client_ip}, User-Agent: {user_agent}")
    
    return {
        "message": "POST received at root endpoint",
        "status": "ok",
        "version": settings.app_version,
    }


if __name__ == "__main__":
    print(f"🌐 Server starting on http://{settings.host}:{settings.port}")
    uvicorn.run(
        "main:app", 
        host=settings.host, 
        port=settings.port, 
        reload=settings.reload,
        log_level="info"  
    )