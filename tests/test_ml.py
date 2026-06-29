"""Tests for the ML pipeline: feature engineering, model training, prediction."""
from __future__ import annotations

import pandas as pd
import numpy as np

from app.ml.feature_engineering import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    generate_synthetic_training_data,
    prepare_inference_features,
    _engineer_features,
)


class TestFeatureEngineering:
    def test_synthetic_data_shape(self) -> None:
        df = generate_synthetic_training_data(n=100)
        assert len(df) == 100
        for col in FEATURE_COLUMNS:
            assert col in df.columns, f"Missing feature column: {col}"
        assert TARGET_COLUMN in df.columns

    def test_synthetic_data_no_nulls(self) -> None:
        df = generate_synthetic_training_data(n=200)
        for col in FEATURE_COLUMNS:
            assert df[col].isnull().sum() == 0, f"Null values in {col}"

    def test_synthetic_data_target_distribution(self) -> None:
        df = generate_synthetic_training_data(n=5000)
        counts = df[TARGET_COLUMN].value_counts()
        # Should have both classes
        assert 0 in counts.index
        assert 1 in counts.index
        # Neither class should dominate >95%
        ratio = counts.min() / counts.max()
        assert ratio > 0.05, f"Target imbalance too extreme: {counts.to_dict()}"

    def test_feature_columns_correct_types(self) -> None:
        df = generate_synthetic_training_data(n=50)
        for col in FEATURE_COLUMNS:
            assert df[col].dtype in [np.int64, np.int32, np.float64, int, float], \
                f"{col} has unexpected dtype: {df[col].dtype}"

    def test_prepare_inference_features(self) -> None:
        # Ensure encoders are populated
        generate_synthetic_training_data(n=50)

        X = prepare_inference_features(
            planned_transit_days=5,
            order_value=1500.0,
            item_count=3,
            discount_rate_avg=0.1,
            shipping_mode="Standard Class",
            region="Western Europe",
            market="Europe",
        )
        assert list(X.columns) == FEATURE_COLUMNS
        assert len(X) == 1
        assert X["planned_transit_days"].iloc[0] == 5
        assert X["order_value"].iloc[0] == 1500.0

    def test_unknown_category_fallback(self) -> None:
        generate_synthetic_training_data(n=50)

        X = prepare_inference_features(
            planned_transit_days=3,
            order_value=500.0,
            item_count=1,
            discount_rate_avg=0.0,
            shipping_mode="Unknown Mode",
            region="Unknown Region",
            market="Unknown Market",
        )
        assert X["shipping_mode_encoded"].iloc[0] == -1
        assert X["region_encoded"].iloc[0] == -1
        assert X["market_encoded"].iloc[0] == -1


class TestModelTraining:
    def test_train_on_synthetic_data(self) -> None:
        """Test that the training pipeline produces a valid model."""
        from app.ml.train_delay_model import train
        metrics = train(use_db=False)

        assert "accuracy" in metrics
        assert "f1" in metrics
        assert "roc_auc" in metrics
        assert metrics["accuracy"] > 0.5, "Model accuracy should be better than random"
        assert metrics["data_source"] == "synthetic"

    def test_model_saved_to_disk(self) -> None:
        """Verify model artifacts are saved after training."""
        from pathlib import Path
        from app.ml.train_delay_model import MODEL_PATH, METADATA_PATH, ENCODERS_PATH, train

        train(use_db=False)

        assert MODEL_PATH.exists(), "Model file not saved"
        assert METADATA_PATH.exists(), "Metadata file not saved"
        assert ENCODERS_PATH.exists(), "Encoders file not saved"


class TestPredictionService:
    def test_stub_prediction_works_without_model(self) -> None:
        """Prediction service should work even when no model is on disk."""
        from app.services.prediction import DelayPredictionService
        from app.api.schemas.prediction import DelayPredictionRequest

        service = DelayPredictionService(db=None)
        request = DelayPredictionRequest(
            supplier_id=1,
            product_id=1,
            region="EMEA",
            lead_time_days=7,
            order_value=12000.0,
            previous_delay_rate=0.12,
            carrier_reliability=0.85,
        )
        response = service.predict_delay(request)
        assert 0.0 <= response.delay_probability <= 1.0
        assert response.predicted_label in {"Delayed", "On-time"}

    def test_model_prediction_after_training(self) -> None:
        """After training, prediction should use the real model."""
        from app.ml.train_delay_model import train
        from app.services.prediction import DelayPredictionService
        from app.api.schemas.prediction import DelayPredictionRequest

        train(use_db=False)

        service = DelayPredictionService(db=None)
        request = DelayPredictionRequest(
            supplier_id=1,
            product_id=1,
            region="Western Europe",
            lead_time_days=10,
            order_value=5000.0,
            previous_delay_rate=0.15,
            carrier_reliability=0.80,
        )
        response = service.predict_delay(request)
        assert 0.0 <= response.delay_probability <= 1.0
        assert response.model_name == "xgboost-delay-v1"
        assert isinstance(response.explanation, dict)
