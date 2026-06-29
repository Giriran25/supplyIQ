from __future__ import annotations

import streamlit as st

from app.streamlit_app.utils import query_copilot


def render() -> None:
    st.title("🤖 AI Executive Copilot")
    st.write("Ask strategic supply chain questions and get data-driven executive summaries.")

    query = st.text_area(
        "Ask a question",
        placeholder="e.g., Why is supplier X risky? What is our current delay rate?",
        height=100,
    )

    if st.button("Ask Copilot", type="primary"):
        if not query.strip():
            st.warning("Please enter a question.")
            return

        with st.spinner("Analyzing your question..."):
            result = query_copilot(query=query.strip())

        if result:
            st.markdown("---")

            # Answer
            st.markdown("### 💡 Answer")
            st.success(result.get("answer", "No answer available."))

            # Supporting metrics
            metrics = result.get("supporting_metrics", {})
            if metrics:
                st.markdown("### 📊 Supporting Metrics")
                cols = st.columns(min(len(metrics), 4))
                for i, (metric_name, metric_value) in enumerate(metrics.items()):
                    with cols[i % len(cols)]:
                        label = metric_name.replace("_", " ").title()
                        if isinstance(metric_value, float) and metric_value < 1:
                            st.metric(label, f"{metric_value:.1%}")
                        else:
                            st.metric(label, f"{metric_value}")

            # Next steps
            next_steps = result.get("next_steps", [])
            if next_steps:
                st.markdown("### 🎯 Recommended Next Steps")
                for i, step in enumerate(next_steps, 1):
                    st.markdown(f"**{i}.** {step}")
        else:
            st.error("Copilot query failed. Is the API server running?")
