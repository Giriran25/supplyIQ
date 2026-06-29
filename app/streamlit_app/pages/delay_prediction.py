from __future__ import annotations

import streamlit as st

from app.streamlit_app.utils import predict_delay, format_percentage


def render() -> None:
    st.title("🔮 Delay Prediction")
    st.write("Predict whether a shipment will be delayed using the production ML model.")

    with st.form("delay_form"):
        col1, col2 = st.columns(2)
        with col1:
            supplier_id = st.number_input("Supplier ID", min_value=1, value=1)
            product_id = st.number_input("Product ID", min_value=1, value=1)
            region = st.text_input("Region", "EMEA")
            lead_time_days = st.number_input("Lead Time (days)", min_value=1, value=7)
        with col2:
            order_value = st.number_input("Order Value ($)", min_value=0.0, value=12000.0, step=100.0)
            previous_delay_rate = st.slider("Previous Delay Rate", 0.0, 1.0, 0.12, step=0.01)
            carrier_reliability = st.slider("Carrier Reliability", 0.0, 1.0, 0.85, step=0.01)

        submitted = st.form_submit_button("Predict Delay")

    if submitted:
        with st.spinner("Running prediction..."):
            result = predict_delay(
                supplier_id=supplier_id,
                product_id=product_id,
                region=region,
                lead_time_days=lead_time_days,
                order_value=order_value,
                previous_delay_rate=previous_delay_rate,
                carrier_reliability=carrier_reliability,
            )

        if result:
            st.markdown("---")
            st.markdown("### Prediction Results")

            col1, col2, col3 = st.columns(3)
            with col1:
                prob = result.get("delay_probability", 0)
                st.metric("Delay Probability", format_percentage(prob))
            with col2:
                label = result.get("predicted_label", "Unknown")
                color = "🔴" if label == "Delayed" else "🟢"
                st.metric("Prediction", f"{color} {label}")
            with col3:
                st.metric("Model", result.get("model_name", "unknown"))

            # Feature importance / explanation
            explanation = result.get("explanation", {})
            if explanation:
                st.markdown("### Feature Impact")
                for feature, impact in explanation.items():
                    feature_label = feature.replace("_", " ").title()
                    st.progress(min(abs(impact), 1.0), text=f"{feature_label}: {impact:.4f}")
        else:
            st.error("Prediction failed. Is the API server running?")
