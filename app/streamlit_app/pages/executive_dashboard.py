from __future__ import annotations

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from app.streamlit_app.utils import get_kpis, get_category_analytics, get_product_analytics, format_currency, format_percentage


def render() -> None:
    st.set_page_config(layout="wide")
    st.title("📊 Executive Dashboard")
    st.subheader("Real-time Supply Chain Intelligence")

    # Sidebar filters
    st.sidebar.markdown("### Filters")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90))
    with col2:
        end_date = st.date_input("End Date", value=datetime.now())

    region = st.sidebar.selectbox(
        "Region",
        ["All", "Americas", "Europe", "Asia Pacific", "Africa", "Middle East"],
        index=0,
    )

    # Convert date to ISO format
    start_date_str = start_date.isoformat() if start_date else None
    end_date_str = end_date.isoformat() if end_date else None
    region_filter = None if region == "All" else region

    # Fetch KPIs
    kpi_data = get_kpis(start_date=start_date_str, end_date=end_date_str, region=region_filter)

    if kpi_data and "kpis" in kpi_data:
        kpis = {kpi["name"]: kpi["value"] for kpi in kpi_data["kpis"]}

        # Display KPI cards
        st.markdown("### Key Performance Indicators")
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.metric("💰 Revenue", format_currency(kpis.get("Revenue", 0)))

        with col2:
            st.metric("📦 Orders", f"{int(kpis.get('Orders', 0)):,}")

        with col3:
            st.metric("👥 Customers", f"{int(kpis.get('Customers', 0)):,}")

        with col4:
            st.metric("🏭 Products", f"{int(kpis.get('Products', 0)):,}")

        with col5:
            delay_rate = kpis.get("Delay Rate", 0)
            st.metric(
                "⚠️ Delay Rate",
                format_percentage(delay_rate),
                delta=f"{delay_rate-0.1:.1%}" if delay_rate > 0.1 else None,
            )

        with col6:
            st.metric("⏱️ Avg Lead Time", f"{kpis.get('Average Lead Time', 0):.1f} days")

        st.markdown("---")

    # Category Analytics
    st.markdown("### Category Performance")
    category_data = get_category_analytics(
        start_date=start_date_str,
        end_date=end_date_str,
        region=region_filter,
        limit=10,
    )

    if category_data and "categories" in category_data:
        categories = category_data["categories"]
        if categories:
            df_categories = pd.DataFrame(categories)

            # Revenue by category (bar chart)
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(data=df_categories.set_index("category_name")["revenue"], use_container_width=True)
                st.caption("Revenue by Category")

            with col2:
                st.bar_chart(data=df_categories.set_index("category_name")["orders_count"], use_container_width=True)
                st.caption("Orders by Category")

            # Category details table
            st.markdown("#### Top Categories")
            display_cols = ["category_name", "orders_count", "revenue", "avg_price", "product_count"]
            df_display = df_categories[display_cols].copy()
            df_display["revenue"] = df_display["revenue"].apply(format_currency)
            df_display["avg_price"] = df_display["avg_price"].apply(format_currency)
            df_display = df_display.rename(columns={
                "category_name": "Category",
                "orders_count": "Orders",
                "revenue": "Revenue",
                "avg_price": "Avg Price",
                "product_count": "Products",
            })
            st.dataframe(df_display, use_container_width=True)

    st.markdown("---")

    # Product Analytics
    st.markdown("### Top Products")
    product_data = get_product_analytics(
        start_date=start_date_str,
        end_date=end_date_str,
        region=region_filter,
        limit=10,
    )

    if product_data and "products" in product_data:
        products = product_data["products"]
        if products:
            df_products = pd.DataFrame(products)

            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(data=df_products.set_index("product_name")["revenue"], use_container_width=True)
                st.caption("Revenue by Product (Top 10)")

            with col2:
                st.bar_chart(data=df_products.set_index("product_name")["units_sold"], use_container_width=True)
                st.caption("Units Sold by Product (Top 10)")

            # Products details table
            st.markdown("#### Top 10 Products by Revenue")
            display_cols = ["product_name", "units_sold", "revenue", "avg_unit_price"]
            df_display = df_products[display_cols].copy()
            df_display["revenue"] = df_display["revenue"].apply(format_currency)
            df_display["avg_unit_price"] = df_display["avg_unit_price"].apply(format_currency)
            df_display = df_display.rename(columns={
                "product_name": "Product",
                "units_sold": "Units Sold",
                "revenue": "Revenue",
                "avg_unit_price": "Avg Price",
            })
            st.dataframe(df_display, use_container_width=True)

    st.markdown("---")
    st.markdown("*Last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
