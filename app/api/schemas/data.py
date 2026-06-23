from __future__ import annotations

from pydantic import BaseModel, Field
from typing import List


class DataUploadRequest(BaseModel):
    dataset_name: str = Field(..., description="Logical dataset name, e.g. shipments")
    csv_payload: str = Field(..., description="Base64-encoded or raw CSV payload")
    source: str = Field("unknown", description="Source system or upload channel")


class DataUploadResponse(BaseModel):
    success: bool
    records_loaded: int
    errors: List[str] = []
