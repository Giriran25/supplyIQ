from __future__ import annotations

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

from app.streamlit_app.utils import get_geography_analytics, format_currency, format_percentage


def render() -> None:
    st.title("🌍 Geography Analytics")
    st.subheader("Regional Performance & Delivery Metrics")

    # Sidebar filters
    st.sidebar.markdown("### Filters")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=90), key="geo_start")
    with col2:
        end_date = st.date_input("End Date", value=datetime.now(), key="geo_end")

    region = st.sidebar.selectbox(
        "Region",
        ["All", "Americas", "Europe", "Asia Pacific", "Africa", "Middle East"],
        index=0,
        key="geo_region",
    )

    # Convert date to ISO format
    start_date_str = start_date.isoformat() if start_date else None
    end_date_str = end_date.isoformat() if end_date else None
    region_filter = None if region == "All" else region

    # Fetch data
    geo_data = get_geography_analytics(
        start_date=start_date_str,
        end_date=end_date_str,
        region=region_filter,
    )

    if geo_data and "geography" in geo_data:
        geography = geo_data["geography"]
        if geography:
            df = pd.DataFrame(geography)

            # Summary metrics
            st.markdown("### Summary Metrics")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Regions", len(df))
            with col2:
                st.metric("Total Revenue", format_currency(df["revenue"].sum()))
            with col3:
                st.metric("Total Orders", f"{int(df['orders'].sum()):,}")
            with col4:
                avg_delay = df["delay_rate"].mean() if len(df) > 0 else 0
                st.metric("Avg Delay Rate", format_percentage(avg_delay))

            st.markdown("---")

            # Charts
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Revenue by Region")
                st.bar_chart(data=df.set_index("region")["revenue"], use_container_width=True)

            with col2:
                st.markdown("#### Orders by Region")
                st.bar_chart(data=df.set_index("region")["orders"], use_container_width=True)

            st.markdown("---")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Delay Rate by Region")
                delay_df = df.set_index("region")["delay_rate"] * 100
                st.bar_chart(data=delay_df, use_container_width=True)

            with col2:
                st.markdown("#### Performance by Region (Revenue vs Delay)")
                # Create scatter plot-like data
                region_perf = df[["region", "revenue", "delay_rate"]].copy()
                region_perf["delay_rate"] = region_perf["delay_rate"] * 100
                st.write(region_perf)

            st.markdown("---")

            # Detailed table
            st.markdown("#### Regional Breakdown")
            display_df = df.copy()
            display_df["revenue"] = display_df["revenue"].apply(format_currency)
            display_df["delay_rate"] = display_df["delay_rate"].apply(format_percentage)
            display_df = display_df.rename(columns={
                "region": "Region",
                "country": "Country",
                "revenue": "Revenue",
                "orders": "Orders",
                "delay_rate": "Delay Rate",
            })
            st.dataframe(display_df, use_container_width=True)

    else:
        st.warning("No geography data available for the selected filters.")

    st.markdown("---")
    st.markdown("*Last updated: {}*".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
