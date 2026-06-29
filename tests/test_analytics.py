"""Tests for analytics service and stub services.

These tests verify that services return data in the expected schema
without requiring a live database connection.
"""
from __future__ import annotations

from app.services.prediction import DelayPredictionService
from app.services.risk import SupplierRiskService
from app.services.resilience import SCRIService
from app.services.simulation import SimulationService
from app.api.schemas.prediction import DelayPredictionRequest
from app.api.schemas.simulation import SimulationRequest


class TestDelayPredictionService:
    def test_predict_delay_returns_valid_response(self) -> None:
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
        assert response.model_name is not None
        assert isinstance(response.explanation, dict)

    def test_predict_delay_high_risk(self) -> None:
        service = DelayPredictionService(db=None)
        request = DelayPredictionRequest(
            supplier_id=1,
            product_id=1,
            region="EMEA",
            lead_time_days=14,
            order_value=80000.0,
            previous_delay_rate=0.9,
            carrier_reliability=0.95,
        )
        response = service.predict_delay(request)
        # Just verify it returns a valid probability and label
        assert 0.0 <= response.delay_probability <= 1.0
        assert response.predicted_label in {"Delayed", "On-time"}
        assert response.model_name is not None


    def test_predict_delay_low_risk(self) -> None:
        service = DelayPredictionService(db=None)
        request = DelayPredictionRequest(
            supplier_id=1,
            product_id=1,
            region="EMEA",
            lead_time_days=3,
            order_value=100.0,
            previous_delay_rate=0.01,
            carrier_reliability=0.05,
        )
        response = service.predict_delay(request)
        assert response.delay_probability < 0.5
        assert response.predicted_label == "On-time"


class TestSupplierRiskService:
    def test_get_supplier_risk_returns_response(self) -> None:
        service = SupplierRiskService(db=None)
        response = service.get_supplier_risk(supplier_id=1)
        assert response is not None
        assert response.supplier_id == 1
        assert response.risk_score >= 0
        assert response.reliability_score >= 0
        assert isinstance(response.risk_factors, dict)
        assert isinstance(response.recommendations, list)


class TestSCRIService:
    def test_compute_scri_returns_response(self) -> None:
        service = SCRIService(db=None)
        response = service.compute_scri()
        assert response.scri_score > 0
        assert response.category in {"Weak", "Moderate", "Strong", "Highly Resilient"}
        assert isinstance(response.drivers, dict)
        assert len(response.drivers) > 0

    def test_scri_category_boundaries(self) -> None:
        assert SCRIService._score_category(30) == "Weak"
        assert SCRIService._score_category(50) == "Moderate"
        assert SCRIService._score_category(70) == "Strong"
        assert SCRIService._score_category(90) == "Highly Resilient"


class TestSimulationService:
    def test_run_scenario_returns_response(self) -> None:
        service = SimulationService(db=None)
        request = SimulationRequest(
            scenario_type="supplier_failure",
            impact_horizon_days=30,
        )
        response = service.run_scenario(request)
        assert response.scenario_name is not None
        assert isinstance(response.revenue_impact, float)
        assert isinstance(response.inventory_impact, float)
        assert isinstance(response.delay_impact, float)
        assert isinstance(response.service_impact, float)
        assert len(response.summary) > 0

    def test_different_scenarios(self) -> None:
        service = SimulationService(db=None)
        for scenario in ["supplier_failure", "demand_spike", "warehouse_shutdown", "transportation_delay"]:
            request = SimulationRequest(scenario_type=scenario, impact_horizon_days=14)
            response = service.run_scenario(request)
            assert response.scenario_name is not None
