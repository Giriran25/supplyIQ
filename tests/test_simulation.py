"""Tests for the simulation service."""
from __future__ import annotations

from app.services.simulation import SimulationService
from app.api.schemas.simulation import SimulationRequest


class TestSimulationService:
    def test_stub_supplier_failure(self) -> None:
        service = SimulationService(db=None)
        request = SimulationRequest(scenario_type="supplier_failure", impact_horizon_days=30)
        response = service._simulate_stub(request)
        assert response.scenario_name == "Supplier Failure"
        assert response.revenue_impact < 0
        assert len(response.summary) > 0
        assert response.resilience_impact < 0
        assert len(response.mitigation_actions) > 0

    def test_stub_demand_spike(self) -> None:
        service = SimulationService(db=None)
        request = SimulationRequest(scenario_type="demand_spike", impact_horizon_days=14)
        response = service._simulate_stub(request)
        assert response.scenario_name == "Demand Spike"
        assert response.revenue_impact < 0  # with horizon < 30 it will scale the base impact
        assert response.resilience_impact < 0

    def test_stub_all_scenarios(self) -> None:
        service = SimulationService(db=None)
        scenarios = ["supplier_failure", "demand_spike", "inventory_shortage", "transportation_disruption", "lead_time_increase"]
        for scenario in scenarios:
            request = SimulationRequest(scenario_type=scenario, impact_horizon_days=30)
            response = service._simulate_stub(request)
            assert response.scenario_name is not None
            assert isinstance(response.revenue_impact, float)
            assert isinstance(response.inventory_impact, float)
            assert isinstance(response.delay_impact, float)
            assert isinstance(response.service_impact, float)
            assert isinstance(response.resilience_impact, float)
            assert isinstance(response.mitigation_actions, list)

    def test_run_scenario_falls_back_to_stub(self) -> None:
        """Without a DB, run_scenario should use the stub."""
        service = SimulationService(db=None)
        request = SimulationRequest(scenario_type="supplier_failure", impact_horizon_days=30)
        response = service.run_scenario(request)
        assert response.scenario_name == "Supplier Failure"
        assert response.revenue_impact != 0

    def test_horizon_scaling(self) -> None:
        """Different horizons should produce different impacts."""
        service = SimulationService(db=None)
        r1 = SimulationRequest(scenario_type="supplier_failure", impact_horizon_days=15)
        r2 = SimulationRequest(scenario_type="supplier_failure", impact_horizon_days=30)
        resp1 = service._simulate_stub(r1)
        resp2 = service._simulate_stub(r2)
        assert resp1.scenario_name == resp2.scenario_name
        assert resp1.revenue_impact > resp2.revenue_impact  # impact is negative, so a smaller horizon means closer to 0
        assert resp1.resilience_impact > resp2.resilience_impact

    def test_summary_contains_scenario_name(self) -> None:
        service = SimulationService(db=None)
        request = SimulationRequest(scenario_type="inventory_shortage", impact_horizon_days=30)
        response = service._simulate_stub(request)
        assert "Inventory Shortage" in response.summary
