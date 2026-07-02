"""AI Copilot service for providing natural language analytics summaries.

Uses the OpenAI API if configured. Otherwise, provides robust deterministic
answers based on existing analytics services to ensure it never fails.
"""
from __future__ import annotations

import json
import logging
from typing import Tuple, List

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment,misc]
from sqlalchemy.orm import Session

from app.api.schemas.copilot import CopilotRequest, CopilotResponse
from app.api.schemas.simulation import SimulationRequest
from app.core.config import settings
from app.services.resilience import SCRIService
from app.services.simulation import SimulationService
from app.services.risk import SupplierRiskService

logger = logging.getLogger("supplychainiq.copilot")


class CopilotService:
    def __init__(self, db: Session) -> None:
        self.db = db
        # Handle case where API key is not provided (e.g., None or empty string)
        self.has_llm = bool(OpenAI is not None and settings.openai_api_key and settings.openai_api_key.strip())
        self.client = OpenAI(api_key=settings.openai_api_key) if self.has_llm else None

    def answer_query(self, request: CopilotRequest) -> CopilotResponse:
        query_lower = request.query.lower()

        # 1. Gather Context from existing business logic
        context_data = self._gather_context(query_lower)

        # 2. Extract metrics for the UI response
        supporting_metrics = self._extract_metrics(context_data)

        # 3. Generate Answer & Next Steps
        if self.has_llm:
            try:
                answer, next_steps = self._generate_with_llm(request.query, context_data)
            except Exception as e:
                logger.error("LLM generation failed: %s. Falling back to deterministic.", e)
                answer, next_steps = self._generate_deterministic(query_lower, context_data)
        else:
            answer, next_steps = self._generate_deterministic(query_lower, context_data)

        return CopilotResponse(
            answer=answer,
            supporting_metrics=supporting_metrics,
            next_steps=next_steps,
        )

    def _gather_context(self, query: str) -> dict:
        """Fetch real data from services to avoid duplicating calculations."""
        context = {}
        
        # Always fetch core baseline metrics & resilience
        scri_service = SCRIService(self.db)
        scri_response = scri_service.compute_scri()
        context["scri"] = scri_response.model_dump()

        sim_service = SimulationService(self.db)
        baseline = sim_service._get_baseline_metrics()
        context["baseline"] = baseline

        # Add simulation context if requested
        if any(kw in query for kw in ["simulate", "twin", "disruption", "failure"]):
            scenario = "supplier_failure"
            if "demand" in query or "spike" in query:
                scenario = "demand_spike"
            elif "transport" in query or "delay" in query:
                scenario = "transportation_disruption"
            elif "shortage" in query or "inventory" in query:
                scenario = "inventory_shortage"
            
            sim_req = SimulationRequest(scenario_type=scenario, impact_horizon_days=30)
            sim_resp = sim_service.run_scenario(sim_req)
            context["simulation"] = sim_resp.model_dump()

        return context

    def _extract_metrics(self, context: dict) -> dict:
        """Extract key numeric metrics to display in the UI."""
        metrics = {}
        if "scri" in context:
            metrics["scri_score"] = context["scri"]["scri_score"]
        if "baseline" in context:
            metrics["delay_rate"] = context["baseline"]["baseline_delay_rate"]
            metrics["total_revenue"] = context["baseline"]["total_revenue"]

        if "simulation" in context:
            metrics["simulated_revenue_impact"] = context["simulation"]["revenue_impact"]
            metrics["simulated_resilience_drop"] = context["simulation"]["resilience_impact"]

        return metrics

    def _generate_deterministic(self, query: str, context: dict) -> Tuple[str, List[str]]:
        """Fallback natural language generator using string templating."""
        scri = context["scri"]
        baseline = context["baseline"]

        if "simulate" in query or "twin" in query or "disruption" in query:
            sim = context.get("simulation", {})
            name = sim.get('scenario_name', 'Simulation')
            ans = (
                f"Based on our Digital Twin, a '{name}' scenario over 30 days would impact "
                f"revenue by ${abs(sim.get('revenue_impact', 0)):,.0f}. "
                f"Resilience would drop by {abs(sim.get('resilience_impact', 0))} points "
                f"and inventory impact is estimated at {sim.get('inventory_impact', 0):.1f}%."
            )
            steps = sim.get("mitigation_actions", ["Activate backup suppliers."])
            return ans, steps

        if "scri" in query or "resilience" in query:
            ans = (
                f"Our current Supply Chain Resilience Index (SCRI) is {scri['scri_score']} "
                f"({scri['category']}). The score is based on 7 core drivers. "
                f"Our strongest driver is {max(scri['drivers'], key=scri['drivers'].get)}."
            )
            steps = [
                "Investigate low-performing resilience drivers in the dashboard.",
                "Run a digital twin simulation for supplier failure.",
                "Check category concentration risks."
            ]
            return ans, steps

        if "delay" in query or "shipment" in query:
            ans = (
                f"Our baseline delay rate is {baseline['baseline_delay_rate']:.1%}. "
                f"Average lead time is {baseline['avg_lead_time']:.1f} days across "
                f"{baseline['total_shipments']} total shipments."
            )
            steps = [
                "Review regional shipping modes to optimize lead times.",
                "Check ML delay predictions for top suppliers.",
                "Consolidate shipments for efficiency."
            ]
            return ans, steps

        if "inventory" in query or "product" in query or "category" in query:
            ans = (
                f"Inventory health is currently driving our resilience score "
                f"with {scri['drivers'].get('Inventory Health', 0)}/10 points. "
                f"Total historical revenue across all products is ${baseline['total_revenue']:,.0f}."
            )
            steps = [
                "Review warehouse capacity and fulfillment bottlenecks.",
                "Ensure safety stock levels align with the recent demand spike."
            ]
            return ans, steps

        # Default fallback
        ans = (
            f"The supply chain is currently operating with an SCRI of {scri['scri_score']} "
            f"and a baseline delay rate of {baseline['baseline_delay_rate']:.1%}."
        )
        steps = [
            "Check the resilience dashboard.",
            "Monitor high-risk shipments using the ML predictor.",
            "Review inventory health."
        ]
        return ans, steps

    def _generate_with_llm(self, query: str, context: dict) -> Tuple[str, List[str]]:
        """Use OpenAI to generate a dynamic executive summary based on data context."""
        system_prompt = (
            "You are an expert Supply Chain AI Copilot for executive leaders. "
            "Use the provided JSON context to answer the user's question accurately. "
            "Never invent metrics or data. Base your answer purely on the context. "
            "Output JSON strictly matching the format: "
            '{"answer": "A concise executive summary", "next_steps": ["Step 1", "Step 2", "Step 3"]}'
        )
        user_prompt = f"Context:\n{json.dumps(context)}\n\nQuestion:\n{query}"

        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )

        raw_json = response.choices[0].message.content
        data = json.loads(raw_json)
        return data.get("answer", "No answer generated."), data.get("next_steps", [])
