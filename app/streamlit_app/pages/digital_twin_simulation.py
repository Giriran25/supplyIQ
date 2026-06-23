from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Digital Twin Simulation")
    st.write("Run disruption scenarios and estimate operational impact.")
    scenario = st.selectbox(
        "Scenario",
        ["Supplier Failure", "Demand Spike", "Warehouse Shutdown", "Transportation Delay"],
    )
    if st.button("Run Simulation"):
        st.success("Scenario simulated: Supplier Failure")
        st.write("Revenue Impact: -$125,000")
        st.write("Inventory Impact: -18.5%")
        st.write("Delay Impact: 18%")
        st.write("Service Impact: 80%")
