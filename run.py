#!/usr/bin/env python3
"""
Main entry point for the Automated Customer Service Agent
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

if __name__ == "__main__":
    # Set environment variables
    os.environ.setdefault("DATABASE_URL", "sqlite:///./customer_service.db")
    os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
