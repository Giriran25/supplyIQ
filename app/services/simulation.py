"""Digital Twin Simulation service.

Runs disruption scenario simulations using real baseline data from the
database when available. Falls back to hardcoded values otherwise.

Supports scenario types:
- supplier_failure: Simulate a key supplier going offline
- demand_spike: Simulate unexpected demand surge
- transportation_disruption: Simulate logistics disruption
- inventory_shortage: Simulate warehouse capacity loss or stockouts
- lead_time_increase: Simulate systemic lead-time delays
"""
from __future__ import annotations

import logging

from sqlalchemy import func, cast, Float, case
from sqlalchemy.orm import Session

from app.api.schemas.simulation import SimulationRequest, SimulationResponse
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.shipment import Shipment

logger = logging.getLogger("supplychainiq.simulation")


# Disruption impact multipliers per scenario type
SCENARIO_IMPACTS = {
    "supplier_failure": {
        "revenue_pct": -0.08,
        "inventory_pct": -0.18,
        "delay_additive": 0.18,
        "service_level": 0.80,
        "resilience_impact": -15.0,
        "mitigation_actions": [
            "Activate secondary regional suppliers",
            "Re-route pending critical orders",
            "Issue customer delay notifications"
        ]
    },
    "demand_spike": {
        "revenue_pct": 0.15,
        "inventory_pct": -0.30,
        "delay_additive": 0.12,
        "service_level": 0.75,
        "resilience_impact": -5.0,
        "mitigation_actions": [
            "Expedite inbound purchase orders",
            "Implement priority-based allocation",
            "Adjust pricing dynamically"
        ]
    },
    "inventory_shortage": {
        "revenue_pct": -0.12,
        "inventory_pct": -0.40,
        "delay_additive": 0.25,
        "service_level": 0.70,
        "resilience_impact": -12.0,
        "mitigation_actions": [
            "Shift fulfillment to alternate distribution centers",
            "Substitute with comparable products",
            "Pause promotions on constrained items"
        ]
    },
    "transportation_disruption": {
        "revenue_pct": -0.05,
        "inventory_pct": -0.10,
        "delay_additive": 0.30,
        "service_level": 0.82,
        "resilience_impact": -8.0,
        "mitigation_actions": [
            "Switch to premium expedited freight modes",
            "Consolidate shipments to maximize throughput",
            "Adjust expected delivery dates dynamically"
        ]
    },
    "lead_time_increase": {
        "revenue_pct": -0.03,
        "inventory_pct": 0.10,  # pipeline inventory increases
        "delay_additive": 0.40,
        "service_level": 0.85,
        "resilience_impact": -6.0,
        "mitigation_actions": [
            "Recalculate safety stock thresholds",
            "Extend order lead-time buffers",
            "Prioritize local sourcing"
        ]
    },
}


class SimulationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def run_scenario(self, request: SimulationRequest) -> SimulationResponse:
        """Run a disruption scenario simulation.

        Fetches baseline metrics from the DB, applies disruption multipliers,
        and scales the impact by the horizon duration.
        """
        try:
            return self._simulate_from_db(request)
        except Exception as exc:
            logger.warning("DB simulation failed: %s. Using stub.", exc)
            return self._simulate_stub(request)

    def _simulate_from_db(self, request: SimulationRequest) -> SimulationResponse:
        """Compute simulation from real baseline data."""
        # Get baseline metrics
        baseline = self._get_baseline_metrics()

        # Get scenario impact multipliers
        impacts = SCENARIO_IMPACTS.get(request.scenario_type, SCENARIO_IMPACTS["supplier_failure"])

        # Scale by horizon (30 days = 1x, shorter = less impact, longer = more)
        horizon_scale = request.impact_horizon_days / 30.0

        # Compute impacts
        revenue_impact = round(baseline["total_revenue"] * impacts["revenue_pct"] * horizon_scale, 2)
        inventory_impact = round(impacts["inventory_pct"] * 100 * horizon_scale, 1)
        delay_impact = round(
            min(1.0, baseline["baseline_delay_rate"] + impacts["delay_additive"] * horizon_scale),
            3,
        )
        service_impact = round(
            max(0.0, impacts["service_level"] - (1 - impacts["service_level"]) * (horizon_scale - 1) * 0.1),
            3,
        )
        resilience_impact = round(impacts["resilience_impact"] * horizon_scale, 1)

        scenario_name = request.scenario_type.replace("_", " ").title()
        summary = (
            f"Simulated '{scenario_name}' over {request.impact_horizon_days} days. "
            f"Baseline revenue: ${baseline['total_revenue']:,.0f}, "
            f"baseline delay rate: {baseline['baseline_delay_rate']:.1%}. "
            f"Projected revenue impact: ${revenue_impact:,.0f}, "
            f"inventory impact: {inventory_impact:.1f}%, "
            f"delay rate increase to {delay_impact:.1%}, "
            f"service level: {service_impact:.1%}."
        )

        return SimulationResponse(
            scenario_name=scenario_name,
            revenue_impact=revenue_impact,
            inventory_impact=inventory_impact,
            delay_impact=delay_impact,
            service_impact=service_impact,
            resilience_impact=resilience_impact,
            mitigation_actions=impacts["mitigation_actions"],
            summary=summary,
        )

    def _get_baseline_metrics(self) -> dict:
        """Fetch baseline metrics from the database."""
        # Total revenue
        total_revenue = float(
            self.db.query(func.coalesce(func.sum(OrderItem.line_total), 0.0)).scalar() or 0.0
        )

        # Delay rate
        ship_stats = (
            self.db.query(
                func.count(Shipment.id).label("total"),
                func.sum(case((Shipment.late_delivery_risk == True, 1), else_=0)).label("late"),
            )
            .one()
        )
        total_shipments = int(ship_stats.total or 0)
        late_shipments = int(ship_stats.late or 0)
        baseline_delay_rate = late_shipments / total_shipments if total_shipments > 0 else 0.12

        # Average lead time
        avg_lead_time = float(
            self.db.query(func.avg(cast(Shipment.actual_transit_days, Float))).scalar() or 5.0
        )

        return {
            "total_revenue": total_revenue,
            "baseline_delay_rate": baseline_delay_rate,
            "avg_lead_time": avg_lead_time,
            "total_shipments": total_shipments,
        }

    def _simulate_stub(self, request: SimulationRequest) -> SimulationResponse:
        """Hardcoded fallback when DB is unavailable."""
        scenario_name = request.scenario_type.replace("_", " ").title()
        impacts = SCENARIO_IMPACTS.get(request.scenario_type, SCENARIO_IMPACTS["supplier_failure"])
        
        horizon_scale = request.impact_horizon_days / 30.0
        revenue_impact = -125000.0 * horizon_scale if request.scenario_type == "supplier_failure" else -75000.0 * horizon_scale
        inventory_impact = impacts["inventory_pct"] * 100 * horizon_scale
        delay_impact = min(1.0, 0.12 + impacts["delay_additive"] * horizon_scale)
        service_impact = impacts["service_level"]
        resilience_impact = impacts["resilience_impact"] * horizon_scale
        
        summary = (
            f"Simulated {scenario_name} for {request.impact_horizon_days} days. "
            f"Revenue impact {revenue_impact:,.0f}, inventory impact {inventory_impact:.1f}%, delay impact {delay_impact*100:.1f}%"
        )
        return SimulationResponse(
            scenario_name=scenario_name,
            revenue_impact=revenue_impact,
            inventory_impact=inventory_impact,
            delay_impact=delay_impact,
            service_impact=service_impact,
            resilience_impact=resilience_impact,
            mitigation_actions=impacts["mitigation_actions"],
            summary=summary,
        )
