from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.schemas.data import DataUploadRequest, DataUploadResponse
from app.core.database import get_db
from app.services.etl import DataIngestionService

router = APIRouter()


@router.post("/upload", response_model=DataUploadResponse)
async def upload_data(request: DataUploadRequest, db: Session = Depends(get_db)) -> DataUploadResponse:
    service = DataIngestionService(db)
    result = service.load_csv(dataset_name=request.dataset_name, csv_payload=request.csv_payload)
    if not result.success:
        raise HTTPException(status_code=400, detail=result.errors)
    return result
