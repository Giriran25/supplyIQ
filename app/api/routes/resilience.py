from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.resilience import SCRIResponse
from app.core.database import get_db
from app.services.resilience import SCRIService

router = APIRouter()


@router.get("/scri", response_model=SCRIResponse)
async def get_scri(db: Session = Depends(get_db)) -> SCRIResponse:
    service = SCRIService(db)
    return service.compute_scri()
