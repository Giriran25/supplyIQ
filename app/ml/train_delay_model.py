"""Train the delay prediction XGBoost model.

Can be run as a script: python -m app.ml.train_delay_model

If a database is available, trains on real data.
Otherwise, trains on synthetic data for demonstration.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from xgboost import XGBClassifier

from app.ml.feature_engineering import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
    build_training_dataset,
    generate_synthetic_training_data,
    SHIPPING_MODE_MAP,
    REGION_MAP,
    MARKET_MAP,
)

logger = logging.getLogger("supplychainiq.ml")

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "delay_model.joblib"
METADATA_PATH = MODEL_DIR / "delay_model_metadata.json"
ENCODERS_PATH = MODEL_DIR / "encoders.json"


def train(use_db: bool = True) -> dict[str, float]:
    """Train the delay prediction model.

    Args:
        use_db: If True, attempt to load data from the database.
                Falls back to synthetic data if the DB is unavailable.

    Returns:
        Dictionary of evaluation metrics.
    """
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Load training data
    df = pd.DataFrame()
    data_source = "synthetic"

    if use_db:
        try:
            from app.core.database import SessionLocal
            with SessionLocal() as db:
                df = build_training_dataset(db)
                if not df.empty:
                    data_source = "database"
                    logger.info("Loaded %d training samples from database", len(df))
        except Exception as exc:
            logger.warning("Could not load from database: %s. Using synthetic data.", exc)

    if df.empty:
        logger.info("Generating synthetic training data")
        df = generate_synthetic_training_data(n=5000)
        data_source = "synthetic"

    # Split features and target
    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    logger.info("Training set shape: %s, Target distribution: %s", X.shape, y.value_counts().to_dict())

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Train XGBoost classifier
    model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        min_child_weight=3,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss",
        use_label_encoder=False,
    )
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "f1": round(f1_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred), 4),
        "recall": round(recall_score(y_test, y_pred), 4),
        "roc_auc": round(roc_auc_score(y_test, y_proba), 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "data_source": data_source,
    }

    logger.info("Model metrics: %s", metrics)

    # Save model
    joblib.dump(model, MODEL_PATH)
    logger.info("Model saved to %s", MODEL_PATH)

    # Save metadata
    metadata = {
        "model_name": "xgboost-delay-v1",
        "trained_at": datetime.utcnow().isoformat(),
        "features": FEATURE_COLUMNS,
        "metrics": metrics,
        "data_source": data_source,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2))

    # Save encoders for inference
    encoders = {
        "shipping_mode": SHIPPING_MODE_MAP,
        "region": REGION_MAP,
        "market": MARKET_MAP,
    }
    ENCODERS_PATH.write_text(json.dumps(encoders, indent=2))
    logger.info("Encoders saved to %s", ENCODERS_PATH)

    # Feature importance
    importances = dict(zip(FEATURE_COLUMNS, model.feature_importances_.tolist()))
    logger.info("Feature importances: %s", importances)

    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    metrics = train(use_db=True)
    print("\n=== Training Complete ===")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
