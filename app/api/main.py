from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import logger
from app.api.health import router as health_router

from contextlib import asynccontextmanager
from app.api.routes import (
    analytics,
    copilot,
    data_platform,
    predictions,
    resilience,
    risk,
    simulation,
    suppliers,
)

from app.core.database import engine
from app.models import Base  # noqa: F401 – ensures all models are registered

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SupplyChainIQ API")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created")
    yield
    logger.info("Shutting down SupplyChainIQ API")

app = FastAPI(
    title="SupplyChainIQ API",
    description="AI-powered supply chain risk intelligence platform",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

from app.core.middleware import LoggingMiddleware
from fastapi.responses import JSONResponse

# CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging middleware
app.add_middleware(LoggingMiddleware)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": {"code": 500, "message": "Internal Server Error"}}
    )

# Health and status
app.include_router(health_router, prefix="/api", tags=["Health"])

# API routes
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(predictions.router, prefix="/api/prediction", tags=["Prediction"])
app.include_router(copilot.router, prefix="/api/copilot", tags=["Copilot"])
app.include_router(data_platform.router, prefix="/api/data", tags=["Data Platform"])
app.include_router(resilience.router, prefix="/api/resilience", tags=["Resilience"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
app.include_router(suppliers.router, prefix="/api/suppliers", tags=["Suppliers"])
