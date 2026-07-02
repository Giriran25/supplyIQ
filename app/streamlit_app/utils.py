"""
Streamlit dashboard utilities for API integration.

Provides caching, error handling, and helper functions for FastAPI calls.
"""

from __future__ import annotations

import streamlit as st
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

import os

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")


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


@st.cache_data(ttl=300)
def get_supplier_risk(supplier_id: int) -> Dict[str, Any] | None:
    """Fetch supplier risk assessment from the risk endpoint."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/risk/supplier/{supplier_id}", timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch supplier risk: {str(e)}")
        return None


@st.cache_data(ttl=300)
def get_scri() -> Dict[str, Any] | None:
    """Fetch Supply Chain Resilience Index from the resilience endpoint."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/api/resilience/scri", timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch SCRI: {str(e)}")
        return None


def run_simulation(
    scenario_type: str,
    supplier_id: Optional[int] = None,
    product_id: Optional[int] = None,
    region: Optional[str] = None,
    impact_horizon_days: int = 30,
) -> Dict[str, Any] | None:
    """Run a disruption scenario simulation."""
    try:
        payload: Dict[str, Any] = {
            "scenario_type": scenario_type,
            "impact_horizon_days": impact_horizon_days,
        }
        if supplier_id is not None:
            payload["supplier_id"] = supplier_id
        if product_id is not None:
            payload["product_id"] = product_id
        if region is not None:
            payload["region"] = region

        response = requests.post(
            f"{API_BASE_URL}/api/simulation/run", json=payload, timeout=15
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to run simulation: {str(e)}")
        return None


def query_copilot(
    query: str,
    context_filter: Optional[Dict[str, str]] = None,
) -> Dict[str, Any] | None:
    """Send a query to the AI Copilot endpoint."""
    try:
        payload: Dict[str, Any] = {"query": query}
        if context_filter:
            payload["context_filter"] = context_filter
        response = requests.post(
            f"{API_BASE_URL}/api/copilot/query", json=payload, timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to query copilot: {str(e)}")
        return None


def format_currency(value: float) -> str:
    """Format value as currency."""
    return f"${value:,.2f}" if value >= 0 else f"-${abs(value):,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage."""
    return f"{value*100:.1f}%"
