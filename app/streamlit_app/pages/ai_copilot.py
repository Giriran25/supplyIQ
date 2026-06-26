from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("AI Executive Copilot")
    st.write("Ask strategic supply chain questions and get executive summaries.")
    query = st.text_area("Ask a question", "Why is supplier X risky?")
    if st.button("Ask Copilot"):
        st.success("Supplier X is rated high risk due to delay frequency and regional concentration.")
        st.write("Supporting metrics: delay rate 18%, SCRI 76, top risk supplier.")
        st.write("Next steps: review alternate supplier options, run supplier failure simulation.")
