#!/usr/bin/env python3
"""
Backend Startup Script
Quick start script for the Backend Layer
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

if __name__ == '__main__':
    import uvicorn
    
    print("\n" + "="*60)
    print("STARTING WEB-BASED VIRTUAL OS BACKEND")
    print("="*60)
    print("API Documentation: http://localhost:8000/docs")
    print("Alternative Docs: http://localhost:8000/redoc")
    print("Health Check: http://localhost:8000/health")
    print("="*60 + "\n")
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # We use our own hot reload
        log_level="info"
    )
