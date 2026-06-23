from __future__ import annotations

import io
import pandas as pd
from sqlalchemy.orm import Session

from app.core.logging import logger


class DataIngestionResult:
    def __init__(self, success: bool, records_loaded: int, errors: list[str]) -> None:
        self.success = success
        self.records_loaded = records_loaded
        self.errors = errors


class DataIngestionService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def load_csv(self, dataset_name: str, csv_payload: str) -> DataIngestionResult:
        try:
            buffer = io.StringIO(csv_payload)
            df = pd.read_csv(buffer)
            logger.info("Loaded CSV for dataset %s with %s rows", dataset_name, len(df))
            # TODO: validate schema, profile data, persist to PostgreSQL
            return DataIngestionResult(success=True, records_loaded=len(df), errors=[])
        except Exception as exc:
            logger.exception("Failed to load CSV payload")
            return DataIngestionResult(success=False, records_loaded=0, errors=[str(exc)])
