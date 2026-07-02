import os
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.models import Order
from app.core.config import settings

router = APIRouter()

START_TIME = datetime.utcnow()


@router.get("/health")
def health_check(db: Session = Depends(get_db)) -> dict:
    """Health check endpoint with system connectivity verification."""
    # Database check
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"disconnected: {str(e)}"

    # ETL status check (are there orders?)
    try:
        order_count = db.query(Order.id).limit(1).scalar()
        etl_status = "ok" if order_count else "no_data"
    except Exception as e:
        etl_status = f"error: {str(e)}"

    # Model availability check
    model_path = os.path.join("models", "delay_model.joblib")
    model_status = "available" if os.path.exists(model_path) else "missing"

    uptime = (datetime.utcnow() - START_TIME).total_seconds()

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "database": db_status,
        "etl_status": etl_status,
        "model_status": model_status,
        "uptime_seconds": round(uptime, 2),
        "version": "0.1.0",
        "service": settings.app_name,
    }
