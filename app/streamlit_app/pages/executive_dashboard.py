from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Executive Dashboard")
    st.subheader("Supply Chain KPI Summary")
    st.metric("Revenue", "$1.2M")
    st.metric("Orders", "4,850")
    st.metric("Delay Rate", "12%")
    st.metric("On-Time Delivery", "88%")
    st.metric("Average Lead Time", "6.4 days")
    st.markdown("---")
    st.markdown("### Strategic Highlights")
    st.write(
        "This dashboard surfaces the most critical supply chain risks, resilience score, and executive insights for rapid decision-making."
    )
