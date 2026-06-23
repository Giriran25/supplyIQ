from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.logging import logger
from app.api.health import router as health_router
from app.api.routes import analytics, predictions


app = FastAPI(
    title="SupplyChainIQ API",
    description="AI-powered supply chain risk intelligence platform",
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
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

# Analytics
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])

# Predictions
app.include_router(predictions.router, prefix="/api/prediction", tags=["Prediction"])


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting SupplyChainIQ API")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    logger.info("Shutting down SupplyChainIQ API")
