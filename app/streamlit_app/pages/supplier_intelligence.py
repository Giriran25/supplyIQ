from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Supplier Intelligence")
    st.write("Analyze supplier reliability, risk scores, and performance drivers.")
    st.subheader("Top Risky Suppliers")
    st.table(
        [
            {"Supplier": "Acme Logistics", "Risk Score": 78.5, "On-Time %": 82},
            {"Supplier": "Global Parts", "Risk Score": 53.0, "On-Time %": 90},
        ]
    )
    st.markdown("---")
    st.subheader("Risk Drivers")
    st.write("Delay frequency, delivery variance, and historical performance feed the intelligence engine.")
