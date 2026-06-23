from __future__ import annotations

from app.api.schemas.simulation import SimulationRequest, SimulationResponse
from sqlalchemy.orm import Session


class SimulationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run_scenario(self, request: SimulationRequest) -> SimulationResponse:
        scenario_name = request.scenario_type.replace("_", " ").title()
        revenue_impact = -125000.0 if request.scenario_type == "supplier_failure" else -75000.0
        inventory_impact = -18.5 if request.scenario_type == "warehouse_shutdown" else -12.3
        delay_impact = 0.18 if request.scenario_type == "transportation_delay" else 0.12
        service_impact = 0.80 if request.scenario_type == "demand_spike" else 0.88
        summary = (
            f"Simulated {scenario_name} for {request.impact_horizon_days} days. "
            f"Revenue down {abs(revenue_impact):,.0f}, inventory impact {inventory_impact}%, delay impact {delay_impact*100:.1f}%"
        )
        return SimulationResponse(
            scenario_name=scenario_name,
            revenue_impact=revenue_impact,
            inventory_impact=inventory_impact,
            delay_impact=delay_impact,
            service_impact=service_impact,
            summary=summary,
        )
