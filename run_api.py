"""
FastAPI application entry point for SupplyChainIQ.

Run with:
  python run_api.py
  
Or with uvicorn directly:
  uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
"""

import uvicorn
from app.core.config import settings


if __name__ == "__main__":
    uvicorn.run(
        "app.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_env == "development",
        log_level=settings.log_level.lower(),
    )
