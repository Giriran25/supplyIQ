"""Feature engineering for delay prediction model.

Extracts features from the database (orders, shipments, order_items)
for training the delay prediction XGBoost classifier.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session


# Feature columns expected by the trained model
FEATURE_COLUMNS = [
    "planned_transit_days",
    "order_value",
    "item_count",
    "discount_rate_avg",
    "shipping_mode_encoded",
    "region_encoded",
    "market_encoded",
]

TARGET_COLUMN = "late_delivery_risk"

# Encoding maps — built during training, used during inference
SHIPPING_MODE_MAP: dict[str, int] = {}
REGION_MAP: dict[str, int] = {}
MARKET_MAP: dict[str, int] = {}


def build_training_dataset(db: Session) -> pd.DataFrame:
    """Query the database and build the training dataset.

    Joins orders, order_items, and shipments to produce one row per shipment
    with relevant features and the binary target (late_delivery_risk).
    """
    query = text("""
        SELECT
            s.id AS shipment_id,
            s.planned_transit_days,
            s.actual_transit_days,
            s.late_delivery_risk,
            s.shipping_mode,
            o.region,
            o.market,
            o.sales_total AS order_value,
            o.profit_amount,
            o.benefit,
            COUNT(oi.id) AS item_count,
            AVG(oi.discount_rate) AS discount_rate_avg,
            AVG(oi.profit_ratio) AS profit_ratio_avg,
            SUM(oi.quantity) AS total_quantity
        FROM shipments s
        JOIN orders o ON o.id = s.order_id
        JOIN order_items oi ON oi.order_id = o.id
        GROUP BY s.id, s.planned_transit_days, s.actual_transit_days,
                 s.late_delivery_risk, s.shipping_mode,
                 o.region, o.market, o.sales_total,
                 o.profit_amount, o.benefit
    """)

    result = db.execute(query)
    rows = result.fetchall()
    columns = result.keys()
    df = pd.DataFrame(rows, columns=columns)

    if df.empty:
        return df

    return _engineer_features(df, fit_encoders=True)


def _engineer_features(df: pd.DataFrame, fit_encoders: bool = False) -> pd.DataFrame:
    """Apply feature transformations to the raw joined data."""
    global SHIPPING_MODE_MAP, REGION_MAP, MARKET_MAP

    if fit_encoders:
        # Build label encoding maps from training data
        SHIPPING_MODE_MAP = {v: i for i, v in enumerate(df["shipping_mode"].unique())}
        REGION_MAP = {v: i for i, v in enumerate(df["region"].unique())}
        MARKET_MAP = {v: i for i, v in enumerate(df["market"].unique())}

    # Apply encodings with fallback to -1 for unknown categories
    df = df.copy()
    df["shipping_mode_encoded"] = df["shipping_mode"].map(SHIPPING_MODE_MAP).fillna(-1).astype(int)
    df["region_encoded"] = df["region"].map(REGION_MAP).fillna(-1).astype(int)
    df["market_encoded"] = df["market"].map(MARKET_MAP).fillna(-1).astype(int)

    # Fill nulls
    df["discount_rate_avg"] = df["discount_rate_avg"].fillna(0.0).astype(float)
    df["item_count"] = df["item_count"].fillna(1).astype(int)
    df["order_value"] = df["order_value"].fillna(0.0).astype(float)
    df["planned_transit_days"] = df["planned_transit_days"].fillna(0).astype(int)

    # Cast target
    df["late_delivery_risk"] = df["late_delivery_risk"].astype(int)

    return df


def prepare_inference_features(
    planned_transit_days: int,
    order_value: float,
    item_count: int,
    discount_rate_avg: float,
    shipping_mode: str,
    region: str,
    market: str,
) -> pd.DataFrame:
    """Build a single-row DataFrame for inference.

    Uses the encoding maps built during training. Falls back to -1
    for unknown categories.
    """
    row = {
        "planned_transit_days": planned_transit_days,
        "order_value": order_value,
        "item_count": item_count,
        "discount_rate_avg": discount_rate_avg,
        "shipping_mode_encoded": SHIPPING_MODE_MAP.get(shipping_mode, -1),
        "region_encoded": REGION_MAP.get(region, -1),
        "market_encoded": MARKET_MAP.get(market, -1),
    }
    return pd.DataFrame([row])[FEATURE_COLUMNS]


def generate_synthetic_training_data(n: int = 5000) -> pd.DataFrame:
    """Generate synthetic training data when no real data is available.

    This allows the model to be trained and tested without a live database.
    """
    rng = np.random.default_rng(42)

    shipping_modes = ["Standard Class", "Second Class", "First Class", "Same Day"]
    regions = ["Western Europe", "Central America", "Eastern Asia", "Southern Asia", "West Africa"]
    markets = ["Europe", "LATAM", "Pacific Asia", "Africa", "USCA"]

    planned_transit = rng.integers(1, 15, size=n)
    order_value = rng.lognormal(mean=6.0, sigma=1.5, size=n).round(2)
    item_count = rng.integers(1, 10, size=n)
    discount_rate = rng.uniform(0.0, 0.25, size=n).round(4)
    shipping_mode = rng.choice(shipping_modes, size=n)
    region = rng.choice(regions, size=n)
    market = rng.choice(markets, size=n)

    # Create target: late delivery correlates with high planned_transit and low-value orders
    delay_prob = (
        0.2
        + 0.03 * planned_transit
        - 0.00001 * order_value
        + 0.1 * (shipping_mode == "Standard Class").astype(float)
        + rng.normal(0, 0.1, size=n)
    )
    late_delivery_risk = (delay_prob > 0.5).astype(int)

    df = pd.DataFrame({
        "planned_transit_days": planned_transit,
        "order_value": order_value,
        "item_count": item_count,
        "discount_rate_avg": discount_rate,
        "shipping_mode": shipping_mode,
        "region": region,
        "market": market,
        "late_delivery_risk": late_delivery_risk,
    })

    return _engineer_features(df, fit_encoders=True)
