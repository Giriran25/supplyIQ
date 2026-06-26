from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import logger
from app.api.health import router as health_router
from app.api.routes import analytics, predictions


from contextlib import asynccontextmanager
from app.api.routes import (
    analytics,
    predictions,
    copilot,
    data_platform,
    resilience,
    risk,
    simulation,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting SupplyChainIQ API")
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

# CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health and status
app.include_router(health_router, tags=["Health"])

# ... inside app initialization area, add routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(predictions.router, prefix="/api/prediction", tags=["Prediction"])
app.include_router(copilot.router, prefix="/api/copilot", tags=["Copilot"])
app.include_router(data_platform.router, prefix="/api/data", tags=["Data Platform"])
app.include_router(resilience.router, prefix="/api/resilience", tags=["Resilience"])
app.include_router(risk.router, prefix="/api/risk", tags=["Risk"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["Simulation"])
