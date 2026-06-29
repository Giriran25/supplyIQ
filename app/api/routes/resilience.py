from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.resilience import SCRIResponse
from app.core.database import get_db
from app.services.resilience import SCRIService

router = APIRouter()


from app.core.cache import resilience_cache

@router.get(
    "/scri", 
    response_model=SCRIResponse,
    summary="Get Supply Chain Resilience Index",
    description="Calculates the organization's SCRI (Supply Chain Resilience Index) based on supplier diversity, geographic concentration, lead-time stability, and inventory health."
)
async def get_scri(db: Session = Depends(get_db)) -> SCRIResponse:
    cache_key = "global_scri"
    if cache_key in resilience_cache:
        return resilience_cache[cache_key]

    service = SCRIService(db)
    result = service.compute_scri()
    
    resilience_cache[cache_key] = result
    return result
