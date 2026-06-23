from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.simulation import SimulationRequest, SimulationResponse
from app.core.database import get_db
from app.services.simulation import SimulationService

router = APIRouter()


@router.post("/run", response_model=SimulationResponse)
async def run_simulation(request: SimulationRequest, db: Session = Depends(get_db)) -> SimulationResponse:
    service = SimulationService(db)
    return service.run_scenario(request)
