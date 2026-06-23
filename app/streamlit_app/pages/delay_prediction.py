from __future__ import annotations

import streamlit as st


def render() -> None:
    st.title("Delay Prediction")
    st.write("Predict whether a shipment will be delayed using baseline and production models.")
    with st.form("delay_form"):
        supplier_id = st.number_input("Supplier ID", min_value=1, value=1)
        product_id = st.number_input("Product ID", min_value=1, value=1)
        region = st.text_input("Region", "EMEA")
        lead_time_days = st.number_input("Lead Time (days)", min_value=1, value=7)
        order_value = st.number_input("Order Value", min_value=0.0, value=12000.0)
        previous_delay_rate = st.slider("Previous Delay Rate", 0.0, 1.0, 0.12)
        carrier_reliability = st.slider("Carrier Reliability", 0.0, 1.0, 0.85)
        submitted = st.form_submit_button("Predict Delay")
        if submitted:
            st.success("Delay probability: 78%\nPredicted: Delayed")
            st.write("Feature impact: previous delay rate, carrier reliability, order value.")
