from __future__ import annotations

import streamlit as st

from app.streamlit_app.pages import (
    executive_dashboard,
    category_analytics,
    product_analytics,
    geography_analytics,
    supplier_intelligence,
    delay_prediction,
    scri_dashboard,
    digital_twin_simulation,
    ai_copilot,
)


PAGES = {
    "📊 Executive Dashboard": executive_dashboard,
    "🏷️ Category Analytics": category_analytics,
    "📦 Product Analytics": product_analytics,
    "🌍 Geography Analytics": geography_analytics,
    "🏭 Supplier Intelligence": supplier_intelligence,
    "🔮 Delay Prediction": delay_prediction,
    "🛡️ SCRI Dashboard": scri_dashboard,
    "🏗️ Digital Twin": digital_twin_simulation,
    "🤖 AI Copilot": ai_copilot,
}


def main() -> None:
    st.set_page_config(page_title="SupplyChainIQ", layout="wide")
    st.sidebar.title("SupplyChainIQ")
    page = st.sidebar.radio("Navigation", list(PAGES.keys()))
    PAGES[page].render()


if __name__ == "__main__":
    main()
