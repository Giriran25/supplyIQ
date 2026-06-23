from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from typing import Any


MASKED_VALUES = {"XXXXXXXXX", "xxxxxxxxx", "N/A", "NA", "NULL", "null"}


def clean_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text if text != "" else None


def normalize_enum(value: Any) -> str | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None
    return cleaned.upper()


def clean_masked_pii(value: Any) -> str | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None
    if cleaned in MASKED_VALUES:
        return None
    return cleaned


def clean_zipcode(value: Any) -> str | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None
    return cleaned


def parse_timestamp(value: str) -> datetime | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None

    candidates = [
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in candidates:
        try:
            parsed = datetime.strptime(cleaned, fmt)
            if parsed.tzinfo is None:
                return parsed.replace(tzinfo=timezone.utc)
            return parsed.astimezone(timezone.utc)
        except ValueError:
            continue

    try:
        parsed = datetime.fromisoformat(cleaned)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def to_int(value: Any) -> int | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None
    try:
        return int(float(cleaned))
    except ValueError:
        return None


def to_decimal(value: Any) -> Decimal | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None
    try:
        return Decimal(cleaned)
    except (InvalidOperation, ValueError):
        return None


def to_boolean(value: Any) -> bool | None:
    cleaned = clean_string(value)
    if cleaned is None:
        return None
    normalized = cleaned.strip().lower()
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no"}:
        return False
    return None


def clean_row(raw: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_type": normalize_enum(raw.get("source_type")),
        "days_for_shipping_real": to_int(raw.get("days_for_shipping_real")),
        "days_for_shipment_scheduled": to_int(raw.get("days_for_shipment_scheduled")),
        "benefit_per_order": to_decimal(raw.get("benefit_per_order")),
        "sales_per_customer": to_decimal(raw.get("sales_per_customer")),
        "delivery_status": normalize_enum(raw.get("delivery_status")),
        "late_delivery_risk": to_boolean(raw.get("late_delivery_risk")),
        "category_id": to_int(raw.get("category_id")),
        "category_name": clean_string(raw.get("category_name")),
        "customer_city": clean_string(raw.get("customer_city")),
        "customer_country": normalize_enum(raw.get("customer_country")),
        "customer_email": clean_masked_pii(raw.get("customer_email")),
        "customer_first_name": clean_string(raw.get("customer_first_name")),
        "customer_id": to_int(raw.get("customer_id")),
        "customer_last_name": clean_string(raw.get("customer_last_name")),
        "customer_password": clean_masked_pii(raw.get("customer_password")),
        "customer_segment": normalize_enum(raw.get("customer_segment")),
        "customer_state": normalize_enum(raw.get("customer_state")),
        "customer_street": clean_string(raw.get("customer_street")),
        "customer_zipcode": clean_zipcode(raw.get("customer_zipcode")),
        "department_id": to_int(raw.get("department_id")),
        "department_name": clean_string(raw.get("department_name")),
        "latitude": to_decimal(raw.get("latitude")),
        "longitude": to_decimal(raw.get("longitude")),
        "market": normalize_enum(raw.get("market")),
        "order_city": clean_string(raw.get("order_city")),
        "order_country": normalize_enum(raw.get("order_country")),
        "order_customer_id": to_int(raw.get("order_customer_id")),
        "order_date": raw.get("order_date"),
        "order_id": to_int(raw.get("order_id")),
        "order_item_cardprod_id": to_int(raw.get("order_item_cardprod_id")),
        "order_item_discount": to_decimal(raw.get("order_item_discount")),
        "order_item_discount_rate": to_decimal(raw.get("order_item_discount_rate")),
        "order_item_id": to_int(raw.get("order_item_id")),
        "order_item_product_price": to_decimal(raw.get("order_item_product_price")),
        "order_item_profit_ratio": to_decimal(raw.get("order_item_profit_ratio")),
        "order_item_quantity": to_int(raw.get("order_item_quantity")),
        "sales": to_decimal(raw.get("sales")),
        "order_item_total": to_decimal(raw.get("order_item_total")),
        "order_profit_per_order": to_decimal(raw.get("order_profit_per_order")),
        "order_region": normalize_enum(raw.get("order_region")),
        "order_state": normalize_enum(raw.get("order_state")),
        "order_status": normalize_enum(raw.get("order_status")),
        "order_zipcode": clean_zipcode(raw.get("order_zipcode")),
        "product_card_id": to_int(raw.get("product_card_id")),
        "product_category_id": to_int(raw.get("product_category_id")),
        "product_description": clean_string(raw.get("product_description")),
        "product_image": clean_string(raw.get("product_image")),
        "product_name": clean_string(raw.get("product_name")),
        "product_price": to_decimal(raw.get("product_price")),
        "product_status": to_int(raw.get("product_status")),
        "shipping_date": raw.get("shipping_date"),
        "shipping_mode": normalize_enum(raw.get("shipping_mode")),
        "source_row_number": raw.get("source_row_number"),
        "source_file_name": raw.get("source_file_name"),
    }
