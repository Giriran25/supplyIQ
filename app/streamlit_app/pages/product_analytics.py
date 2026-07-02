from __future__ import annotations

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from app.streamlit_app.utils import get_product_analytics, format_currency


def render() -> None:
    st.title("📦 Product Analytics")
    st.subheader("Product Performance & Sales Trends")

    # Sidebar filters
    st.sidebar.markdown("### Filters")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90), key="product_start")
    with col2:
        end_date = st.date_input("End Date", value=datetime.now(), key="product_end")

    region = st.sidebar.selectbox(
        "Region",
        ["All", "Americas", "Europe", "Asia Pacific", "Africa", "Middle East"],
        index=0,
        key="product_region",
    )
    limit = st.sidebar.slider("Top N Products", 10, 200, 50)

    # Convert date to ISO format
    start_date_str = start_date.isoformat() if start_date else None
    end_date_str = end_date.isoformat() if end_date else None
    region_filter = None if region == "All" else region

    # Fetch data
    product_data = get_product_analytics(
        start_date=start_date_str,
        end_date=end_date_str,
        region=region_filter,
        limit=limit,
    )

    if product_data and "products" in product_data:
        products = product_data["products"]
        if products:
            df = pd.DataFrame(products)

            # Summary metrics
            st.markdown("### Summary Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Products", len(df))
            with col2:
                st.metric("Total Revenue", format_currency(df["revenue"].sum()))
            with col3:
                st.metric("Total Units Sold", f"{int(df['units_sold'].sum()):,}")
            with col4:
                st.metric("Avg Price per Unit", format_currency(df["avg_unit_price"].mean()))

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Revenue Distribution")
                st.bar_chart(data=df.head(20).set_index("product_name")["revenue"], use_container_width=True)

            with col2:
                st.markdown("#### Units Sold Distribution")
                st.bar_chart(data=df.head(20).set_index("product_name")["units_sold"], use_container_width=True)

            st.markdown("---")

            # Detailed table
            st.markdown("#### All Products (Sorted by Revenue)")
            display_df = df.copy()
            display_df["revenue"] = display_df["revenue"].apply(format_currency)
            display_df["avg_unit_price"] = display_df["avg_unit_price"].apply(format_currency)
            display_df = display_df.rename(columns={
                "product_name": "Product",
                "units_sold": "Units",
                "revenue": "Revenue",
                "avg_unit_price": "Avg Price",
            })
            display_df = display_df[["product_id", "Product", "Units", "Revenue", "Avg Price"]]
            st.dataframe(display_df, use_container_width=True)

    else:
        st.warning("No product data available for the selected filters.")

    st.markdown("---")
    st.markdown("*Last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
