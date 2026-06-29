from __future__ import annotations

import streamlit as st

from app.streamlit_app.utils import get_supplier_risk, format_percentage


def render() -> None:
    st.title("🏭 Supplier Intelligence")
    st.write("Analyze supplier reliability, risk scores, and performance drivers.")

    # Supplier selection
    st.sidebar.markdown("### Supplier Selection")
    supplier_id = st.sidebar.number_input("Supplier ID", min_value=1, value=1, step=1)

    with st.spinner("Fetching supplier risk data..."):
        risk_data = get_supplier_risk(supplier_id)

    if risk_data:
        st.markdown("### Supplier Risk Assessment")

        # Header metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Supplier", risk_data.get("supplier_name", "Unknown"))
        with col2:
            risk_score = risk_data.get("risk_score", 0)
            risk_label = "🔴 High" if risk_score > 70 else ("🟡 Medium" if risk_score > 40 else "🟢 Low")
            st.metric("Risk Score", f"{risk_score:.1f}", delta=risk_label)
        with col3:
            reliability = risk_data.get("reliability_score", 0)
            st.metric("Reliability", f"{reliability:.1f}%")

        st.markdown("---")

        # Risk factors
        st.markdown("### Risk Drivers")
        risk_factors = risk_data.get("risk_factors", {})
        if risk_factors:
            cols = st.columns(len(risk_factors))
            for i, (factor, value) in enumerate(risk_factors.items()):
                with cols[i]:
                    factor_label = factor.replace("_", " ").title()
                    st.metric(factor_label, f"{value:.3f}")

        st.markdown("---")

        # Recommendations
        st.markdown("### Recommendations")
        recommendations = risk_data.get("recommendations", [])
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")
    else:
        st.info("Enter a supplier ID in the sidebar and ensure the API server is running.")
