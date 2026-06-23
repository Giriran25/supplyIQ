"""
Streamlit dashboard utilities for API integration.

Provides caching, error handling, and helper functions for FastAPI calls.
"""

from __future__ import annotations

import streamlit as st
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


API_BASE_URL = "http://localhost:8000"


@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_kpis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
) -> Dict[str, Any] | None:
    """Fetch KPIs from the analytics endpoint."""
    try:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "region": region,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(f"{API_BASE_URL}/api/analytics/kpis", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch KPIs: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_category_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 50,
) -> Dict[str, Any] | None:
    """Fetch category analytics from the analytics endpoint."""
    try:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "region": region,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(f"{API_BASE_URL}/api/analytics/categories", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch category analytics: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_product_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 100,
) -> Dict[str, Any] | None:
    """Fetch product analytics from the analytics endpoint."""
    try:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "region": region,
            "limit": limit,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(f"{API_BASE_URL}/api/analytics/products", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch product analytics: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_geography_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    region: Optional[str] = None,
) -> Dict[str, Any] | None:
    """Fetch geography analytics from the analytics endpoint."""
    try:
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "region": region,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(f"{API_BASE_URL}/api/analytics/geography", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch geography analytics: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_shipment_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Dict[str, Any] | None:
    """Fetch shipment analytics from the analytics endpoint."""
    try:
        params = {
            "start_date": start_date,
            "end_date": end_date,
        }
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(f"{API_BASE_URL}/api/analytics/shipments", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch shipment analytics: {str(e)}")
        return None


def predict_delay(
    supplier_id: int,
    product_id: int,
    region: str,
    lead_time_days: int,
    order_value: float,
    previous_delay_rate: float,
    carrier_reliability: float,
) -> Dict[str, Any] | None:
    """Predict delivery delay for an order."""
    try:
        payload = {
            "supplier_id": supplier_id,
            "product_id": product_id,
            "region": region,
            "lead_time_days": lead_time_days,
            "order_value": order_value,
            "previous_delay_rate": previous_delay_rate,
            "carrier_reliability": carrier_reliability,
        }
        response = requests.post(f"{API_BASE_URL}/api/prediction/delay", json=payload, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to predict delay: {str(e)}")
        return None


def format_currency(value: float) -> str:
    """Format value as currency."""
    return f"${value:,.2f}" if value >= 0 else f"-${abs(value):,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value*100:.1f}%"
