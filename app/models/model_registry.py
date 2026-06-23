from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass
class ModelRecord:
    model_name: str
    version: str
    training_date: datetime
    metrics: dict[str, float]
    features: list[str]
    artifact_path: Path


class ModelRegistry:
    def __init__(self, registry_path: Path = Path("models")) -> None:
        self.registry_path = registry_path
        self.registry_path.mkdir(parents=True, exist_ok=True)
        self.records: list[ModelRecord] = []

    def register(self, record: ModelRecord) -> None:
        self.records.append(record)

    def latest(self, model_name: str) -> ModelRecord | None:
        candidates = [r for r in self.records if r.model_name == model_name]
        return max(candidates, key=lambda r: r.training_date) if candidates else None
