from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.routes.analytics import router as analytics_router
from app.api.routes.suppliers import router as suppliers_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="SupplyChainIQ API")
    app.include_router(health_router)
    app.include_router(analytics_router, prefix="/api/analytics")
    app.include_router(suppliers_router, prefix="/suppliers")

    @app.on_event("startup")
    def startup():
        # future: connect to services, warmups
        pass

    return app


app = create_app()
from __future__ import annotations

from fastapi import FastAPI

from app.core.logging import logger
from app.api.routes import data_platform, analytics, predictions, risk, resilience, simulation, copilot


app = FastAPI(
    title="SupplyChainIQ API",
    description="AI-powered supply chain risk intelligence platform",
    version="0.1.0",
)

app.include_router(data_platform.router, prefix="/api/data", tags=["data"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(predictions.router, prefix="/api/prediction", tags=["prediction"])
app.include_router(risk.router, prefix="/api/risk", tags=["risk"])
app.include_router(resilience.router, prefix="/api/resilience", tags=["resilience"])
app.include_router(simulation.router, prefix="/api/simulation", tags=["simulation"])
app.include_router(copilot.router, prefix="/api/copilot", tags=["copilot"])


@app.on_event("startup")
async def startup_event() -> None:
    logger.info("Starting SupplyChainIQ API")
