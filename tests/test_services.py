from app.services.prediction import DelayPredictionService
from app.api.schemas.prediction import DelayPredictionRequest


def test_delay_prediction_service() -> None:
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
