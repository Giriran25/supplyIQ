from __future__ import annotations

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from app.streamlit_app.utils import get_category_analytics, format_currency


def render() -> None:
    st.title("🏷️ Category Analytics")
    st.subheader("Category Performance & Market Breakdown")

    # Sidebar filters
    st.sidebar.markdown("### Filters")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90), key="cat_start")
    with col2:
        end_date = st.date_input("End Date", value=datetime.now(), key="cat_end")

    region = st.sidebar.selectbox(
        "Region",
        ["All", "Americas", "Europe", "Asia Pacific", "Africa", "Middle East"],
        index=0,
        key="cat_region",
    )
    limit = st.sidebar.slider("Categories to Show", 10, 100, 50)

    # Convert date to ISO format
    start_date_str = start_date.isoformat() if start_date else None
    end_date_str = end_date.isoformat() if end_date else None
    region_filter = None if region == "All" else region

    # Fetch data
    category_data = get_category_analytics(
        start_date=start_date_str,
        end_date=end_date_str,
        region=region_filter,
        limit=limit,
    )

    if category_data and "categories" in category_data:
        categories = category_data["categories"]
        if categories:
            df = pd.DataFrame(categories)

            # Summary metrics
            st.markdown("### Summary Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Categories", len(df))
            with col2:
                st.metric("Total Revenue", format_currency(df["revenue"].sum()))
            with col3:
                st.metric("Total Orders", f"{int(df['orders_count'].sum()):,}")
            with col4:
                st.metric("Avg Category Price", format_currency(df["avg_price"].mean()))

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Revenue by Category")
                st.bar_chart(data=df.set_index("category_name")["revenue"], use_container_width=True)

            with col2:
                st.markdown("#### Orders by Category")
                st.bar_chart(data=df.set_index("category_name")["orders_count"], use_container_width=True)

            st.markdown("---")

            # Market share pie chart
            st.markdown("#### Market Share by Revenue")
            fig_data = df.set_index("category_name")["revenue"]
            st.bar_chart(fig_data, use_container_width=True)

            st.markdown("---")

            # Detailed table
            st.markdown("#### All Categories (Sorted by Revenue)")
            display_df = df.copy()
            display_df["revenue"] = display_df["revenue"].apply(format_currency)
            display_df["avg_price"] = display_df["avg_price"].apply(format_currency)
            display_df = display_df.rename(columns={
                "category_name": "Category",
                "product_count": "Products",
                "orders_count": "Orders",
                "revenue": "Revenue",
                "avg_price": "Avg Price",
            })
            display_df = display_df[["category_id", "Category", "Products", "Orders", "Revenue", "Avg Price"]]
            st.dataframe(display_df, use_container_width=True)

    else:
        st.warning("No category data available for the selected filters.")

    st.markdown("---")
    st.markdown("*Last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
