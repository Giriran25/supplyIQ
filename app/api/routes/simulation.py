from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.simulation import SimulationRequest, SimulationResponse
from app.core.database import get_db
from app.services.simulation import SimulationService

router = APIRouter()


from app.core.cache import simulation_cache
import hashlib

@router.post(
    "/run", 
    response_model=SimulationResponse,
    summary="Run Supply Chain Simulation",
    description="Simulates supply chain disruptions such as supplier failures, demand spikes, or logistics delays based on a specified horizon."
)
async def run_simulation(request: SimulationRequest, db: Session = Depends(get_db)) -> SimulationResponse:
    # Build cache key from request parameters
    req_str = f"{request.scenario_type}_{request.horizon_days}_{request.supplier_id}_{request.demand_multiplier}"
    cache_key = hashlib.md5(req_str.encode()).hexdigest()
    
    if cache_key in simulation_cache:
        return simulation_cache[cache_key]

    service = SimulationService(db)
    result = service.run_scenario(request)
    
    simulation_cache[cache_key] = result
    return result
