from __future__ import annotations

import streamlit as st

from app.streamlit_app.utils import run_simulation, format_currency, format_percentage


SCENARIO_MAP = {
    "Supplier Failure": "supplier_failure",
    "Demand Spike": "demand_spike",
    "Warehouse Shutdown": "warehouse_shutdown",
    "Transportation Delay": "transportation_delay",
}


def render() -> None:
    st.title("🏗️ Digital Twin Simulation")
    st.write("Run disruption scenarios and estimate operational impact on your supply chain.")

    with st.form("simulation_form"):
        col1, col2 = st.columns(2)
        with col1:
            scenario_label = st.selectbox("Scenario Type", list(SCENARIO_MAP.keys()))
            impact_horizon = st.slider("Impact Horizon (days)", 7, 90, 30)
        with col2:
            supplier_id = st.number_input("Supplier ID (optional)", min_value=0, value=0, help="Set to 0 to skip")
            region = st.text_input("Region (optional)", "", help="Leave blank to skip")

        submitted = st.form_submit_button("Run Simulation")

    if submitted:
        scenario_type = SCENARIO_MAP[scenario_label]
        sup_id = supplier_id if supplier_id > 0 else None
        reg = region.strip() if region.strip() else None

        with st.spinner(f"Simulating {scenario_label}..."):
            result = run_simulation(
                scenario_type=scenario_type,
                supplier_id=sup_id,
                region=reg,
                impact_horizon_days=impact_horizon,
            )

        if result:
            st.markdown("---")
            st.markdown(f"### Scenario: {result.get('scenario_name', scenario_label)}")

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                rev_impact = result.get("revenue_impact", 0)
                st.metric("💰 Revenue Impact", format_currency(rev_impact))
            with col2:
                inv_impact = result.get("inventory_impact", 0)
                st.metric("📦 Inventory Impact", f"{inv_impact:.1f}%")
            with col3:
                delay_impact = result.get("delay_impact", 0)
                st.metric("⏱️ Delay Impact", format_percentage(delay_impact))
            with col4:
                service_impact = result.get("service_impact", 0)
                st.metric("📊 Service Level", format_percentage(service_impact))

            st.markdown("---")
            st.markdown("### Summary")
            st.info(result.get("summary", "No summary available."))
        else:
            st.error("Simulation failed. Is the API server running?")
