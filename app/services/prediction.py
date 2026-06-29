"""Delay prediction service.

Loads a trained XGBoost model from disk and uses it for inference.
Falls back to the formula-based stub if no trained model is available.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import joblib
from sqlalchemy.orm import Session

from app.api.schemas.prediction import DelayPredictionRequest, DelayPredictionResponse

logger = logging.getLogger("supplychainiq.prediction")

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "delay_model.joblib"
METADATA_PATH = MODEL_DIR / "delay_model_metadata.json"
ENCODERS_PATH = MODEL_DIR / "encoders.json"


class DelayPredictionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._model = None
        self._metadata = None
        self._encoders = None
        self._load_model()

    def _load_model(self) -> None:
        """Attempt to load the trained model and encoders from disk."""
        try:
            if MODEL_PATH.exists():
                self._model = joblib.load(MODEL_PATH)
                logger.info("Loaded trained model from %s", MODEL_PATH)
            if METADATA_PATH.exists():
                self._metadata = json.loads(METADATA_PATH.read_text())
            if ENCODERS_PATH.exists():
                self._encoders = json.loads(ENCODERS_PATH.read_text())
        except Exception as exc:
            logger.warning("Could not load trained model: %s. Using stub.", exc)
            self._model = None

    def predict_delay(self, request: DelayPredictionRequest) -> DelayPredictionResponse:
        if self._model is not None and self._encoders is not None:
            return self._predict_with_model(request)
        return self._predict_stub(request)

    def _predict_with_model(self, request: DelayPredictionRequest) -> DelayPredictionResponse:
        """Use the trained XGBoost model for prediction."""
        from app.ml.feature_engineering import FEATURE_COLUMNS

        # Map request fields to model features
        shipping_mode_map = self._encoders.get("shipping_mode", {})
        region_map = self._encoders.get("region", {})
        market_map = self._encoders.get("market", {})

        features = {
            "planned_transit_days": request.lead_time_days,
            "order_value": request.order_value,
            "item_count": 1,  # default for single-item inference
            "discount_rate_avg": 0.0,  # not available in request
            "shipping_mode_encoded": shipping_mode_map.get("Standard Class", 0),
            "region_encoded": region_map.get(request.region, -1),
            "market_encoded": market_map.get(request.region, -1),
        }

        import pandas as pd
        X = pd.DataFrame([features])[FEATURE_COLUMNS]

        # Get probability
        proba = self._model.predict_proba(X)[0]
        delay_probability = float(proba[1])  # P(late=1)
        predicted_label = "Delayed" if delay_probability >= 0.5 else "On-time"

        # Feature importance from the trained model
        feature_importance = dict(zip(
            FEATURE_COLUMNS,
            [round(float(v), 4) for v in self._model.feature_importances_]
        ))

        model_name = self._metadata.get("model_name", "xgboost-delay-v1") if self._metadata else "xgboost-delay-v1"

        return DelayPredictionResponse(
            delay_probability=round(delay_probability, 4),
            predicted_label=predicted_label,
            model_name=model_name,
            explanation=feature_importance,
        )

    def _predict_stub(self, request: DelayPredictionRequest) -> DelayPredictionResponse:
        """Fallback: formula-based prediction when no trained model is available."""
        delay_probability = min(max(
            request.previous_delay_rate * 0.6
            + request.carrier_reliability * 0.2
            + request.order_value / 100000,
            0.0
        ), 1.0)
        predicted_label = "Delayed" if delay_probability >= 0.5 else "On-time"
        explanation = {
            "previous_delay_rate": round(request.previous_delay_rate * 0.6, 4),
            "carrier_reliability": round(request.carrier_reliability * 0.2, 4),
            "order_value": round(request.order_value / 100000, 4),
        }
        return DelayPredictionResponse(
            delay_probability=round(delay_probability, 4),
            predicted_label=predicted_label,
            model_name="xgboost-production-stub",
            explanation=explanation,
        )
