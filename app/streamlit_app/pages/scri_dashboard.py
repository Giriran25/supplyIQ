from __future__ import annotations

import streamlit as st
import pandas as pd

from app.streamlit_app.utils import get_scri


def render() -> None:
    st.title("🛡️ Supply Chain Resilience Index")
    st.write("SCRI summarizes supply chain resilience across diversity, stability, and reliability.")

    with st.spinner("Computing SCRI..."):
        scri_data = get_scri()

    if scri_data:
        # Header metrics
        col1, col2 = st.columns(2)
        with col1:
            score = scri_data.get("scri_score", 0)
            st.metric("SCRI Score", f"{score:.1f}")
        with col2:
            category = scri_data.get("category", "Unknown")
            color = {"Weak": "🔴", "Moderate": "🟡", "Strong": "🟢", "Highly Resilient": "💎"}.get(category, "⚪")
            st.metric("Category", f"{color} {category}")

        st.markdown("---")

        # Driver composition
        st.markdown("### Driver Composition")
        drivers = scri_data.get("drivers", {})
        if drivers:
            df_drivers = pd.DataFrame(
                [{"Driver": k, "Score": v} for k, v in drivers.items()]
            )
            st.bar_chart(data=df_drivers.set_index("Driver")["Score"], use_container_width=True)

            # Detailed table
            st.markdown("#### Driver Scores")
            st.dataframe(df_drivers, use_container_width=True)

        st.markdown("---")

        # Validation notes
        notes = scri_data.get("validation_notes", "")
        if notes:
            st.info(f"**Methodology**: {notes}")

        # Recommendations based on lowest drivers
        if drivers:
            sorted_drivers = sorted(drivers.items(), key=lambda x: x[1])
            st.markdown("### Improvement Priorities")
            for name, score in sorted_drivers[:3]:
                st.markdown(f"- **{name}** (score: {score:.1f}) — consider targeted improvement actions")
    else:
        st.warning("SCRI data not available. Ensure the API server is running.")
