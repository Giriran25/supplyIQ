from __future__ import annotations

from pydantic import BaseModel
from typing import Dict, List, Optional


class CopilotRequest(BaseModel):
    query: str
    context_filter: Optional[Dict[str, str]] = None


class CopilotResponse(BaseModel):
    answer: str
    supporting_metrics: Dict[str, float]
    next_steps: List[str]
