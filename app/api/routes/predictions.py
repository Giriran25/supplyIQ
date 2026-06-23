from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.prediction import DelayPredictionRequest, DelayPredictionResponse
from app.core.database import get_db
from app.services.prediction import DelayPredictionService

router = APIRouter()


@router.post("/delay", response_model=DelayPredictionResponse)
async def predict_delay(request: DelayPredictionRequest, db: Session = Depends(get_db)) -> DelayPredictionResponse:
    service = DelayPredictionService(db)
    return service.predict_delay(request)
