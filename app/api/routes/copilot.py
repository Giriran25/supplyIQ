from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas.copilot import CopilotRequest, CopilotResponse
from app.core.database import get_db
from app.services.copilot import CopilotService

router = APIRouter()


@router.post("/query", response_model=CopilotResponse)
async def query_copilot(request: CopilotRequest, db: Session = Depends(get_db)) -> CopilotResponse:
    service = CopilotService(db)
    return service.answer_query(request)
