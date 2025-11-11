"""
Backend Layer - FastAPI Main Application
Entry point for the Web-Based Virtual OS Backend API
"""

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.os_connector import os_connector
from backend.services.hot_reload import HotReloadService
from backend.routers import system_router, shell_router, file_router, process_router


# Hot reload service instance
hot_reload_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    print("\n" + "="*60)
    print("BACKEND LAYER STARTING")
    print("="*60)
    
    # OS is already initialized by os_connector import
    print("✓ Core OS Layer connected")
    
    # Start hot reload if enabled
    global hot_reload_service
    try:
        ai_os_path = Path(__file__).parent.parent / "ai_os"
        hot_reload_service = HotReloadService(
            watch_path=str(ai_os_path),
            reload_callback=lambda: os_connector.reload_os()
        )
        hot_reload_service.start()
        print("✓ Hot reload service started")
    except Exception as e:
        print(f"⚠ Hot reload not available: {e}")
    
    print("="*60)
    print("BACKEND LAYER READY")
    print("="*60)
    print(f"API Documentation: http://localhost:8000/docs")
    print(f"Alternative Docs: http://localhost:8000/redoc")
    print("="*60 + "\n")
    
    yield
    
    # Shutdown
    print("\n" + "="*60)
    print("BACKEND LAYER SHUTTING DOWN")
    print("="*60)
    
    if hot_reload_service:
        hot_reload_service.stop()
        print("✓ Hot reload service stopped")
    
    os_connector.shutdown()
    print("✓ Core OS Layer disconnected")
    
    print("="*60)
    print("BACKEND LAYER SHUTDOWN COMPLETE")
    print("="*60 + "\n")


# Create FastAPI application
app = FastAPI(
    title="Web-Based Virtual OS - Backend API",
    description="REST API layer for the modular Web-Based Virtual Operating System",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(system_router.router)
app.include_router(shell_router.router)
app.include_router(file_router.router)
app.include_router(process_router.router)


@app.get("/")
async def root():
    """
    Root endpoint - API information
    """
    return {
        "name": "Web-Based Virtual OS - Backend API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "system": "/system",
            "shell": "/shell",
            "files": "/files",
            "process": "/process"
        }
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        os_info = os_connector.get_system_info()
        return {
            "status": "healthy",
            "os_initialized": os_info.get("initialized", False),
            "uptime_seconds": os_info.get("uptime_seconds", 0)
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.get("/hot-reload/status")
async def hot_reload_status():
    """
    Get hot reload service status
    """
    if hot_reload_service:
        return hot_reload_service.get_status()
    else:
        return {
            "enabled": False,
            "message": "Hot reload service not available"
        }


@app.post("/hot-reload/trigger")
async def trigger_hot_reload():
    """
    Manually trigger a hot reload
    """
    try:
        result = os_connector.reload_os()
        return result
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": str(e)
            }
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url)
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An internal error occurred"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("STARTING WEB-BASED VIRTUAL OS BACKEND")
    print("="*60 + "\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # We use our own hot reload
        log_level="info"
    )
