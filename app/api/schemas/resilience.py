from __future__ import annotations

from pydantic import BaseModel
from typing import Dict


class SCRIResponse(BaseModel):
    scri_score: float
    category: str
    drivers: Dict[str, float]
    validation_notes: str
