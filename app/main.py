from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.mongodb import init_db
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB connection
    await init_db()
    
    # Start APScheduler background agent
    from app.services.scheduler_service import start_scheduler
    start_scheduler()
    
    yield
    
    # Shutdown: Stop APScheduler background agent
    from app.services.scheduler_service import shutdown_scheduler
    shutdown_scheduler()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    description="A production-ready REST API for AI Job Agent",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

@app.get("/")
async def root():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME
    }

@app.get("/debug/config")
async def debug_config():
    try:
        from app.models.resume import Resume
        Resume.get_pymongo_collection()
        mongodb_loaded = True
    except Exception:
        mongodb_loaded = False

    return {
        "gemini_key_loaded": bool(settings.GEMINI_API_KEY),
        "mongodb_loaded": mongodb_loaded,
        "project_name": settings.PROJECT_NAME
    }

@app.get("/debug/models")
async def debug_models():
    return {
        "gemini_model": settings.GEMINI_MODEL
    }
