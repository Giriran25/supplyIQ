from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass
from typing import Iterable


DATE_FORMATS = [
    "%m/%d/%Y %H:%M",
    "%m/%d/%Y %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
    "%Y-%m-%dT%H:%M:%S%z",
]


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[str]


def validate_required(value: str | None) -> bool:
    return value is not None and str(value).strip() != ""


def validate_int(value: str | None, required: bool = True) -> bool:
    if not validate_required(value):
        return not required
    try:
        int(str(value).strip())
        return True
    except ValueError:
        return False


def validate_float(value: str | None, required: bool = True) -> bool:
    if not validate_required(value):
        return not required
    try:
        float(str(value).strip())
        return True
    except ValueError:
        return False


def validate_boolean_int(value: str | None, required: bool = True) -> bool:
    if not validate_required(value):
        return not required
    return str(value).strip() in {"0", "1", "True", "False", "true", "false"}


def validate_datetime(value: str | None, required: bool = True) -> bool:
    if not validate_required(value):
        return not required
    normalized = str(value).strip()
    for fmt in DATE_FORMATS:
        try:
            datetime.strptime(normalized, fmt)
            return True
        except ValueError:
            continue
    return False


def validate_latitude(value: str | None, required: bool = True) -> bool:
    if not validate_required(value):
        return not required
    try:
        lat = float(str(value).strip())
    except ValueError:
        return False
    return -90.0 <= lat <= 90.0


def validate_longitude(value: str | None, required: bool = True) -> bool:
    if not validate_required(value):
        return not required
    try:
        lon = float(str(value).strip())
    except ValueError:
        return False
    return -180.0 <= lon <= 180.0


def validate_row(row: dict[str, str]) -> ValidationResult:
    errors: list[str] = []

    if not validate_required(row.get("source_type")):
        errors.append("TYPE_REQUIRED")
    if not validate_int(row.get("days_for_shipping_real")):
        errors.append("DAYS_FOR_SHIPPING_INVALID")
    if not validate_int(row.get("days_for_shipment_scheduled")):
        errors.append("DAYS_FOR_SHIPMENT_INVALID")
    if not validate_float(row.get("benefit_per_order")):
        errors.append("BENEFIT_INVALID")
    if not validate_float(row.get("sales_per_customer")):
        errors.append("SALES_PER_CUSTOMER_INVALID")
    if not validate_required(row.get("delivery_status")):
        errors.append("DELIVERY_STATUS_REQUIRED")
    if not validate_boolean_int(row.get("late_delivery_risk")):
        errors.append("LATE_DELIVERY_RISK_INVALID")
    if not validate_int(row.get("category_id")):
        errors.append("CATEGORY_ID_INVALID")
    if not validate_required(row.get("category_name")):
        errors.append("CATEGORY_NAME_REQUIRED")
    if not validate_required(row.get("customer_city")):
        errors.append("CUSTOMER_CITY_REQUIRED")
    if not validate_required(row.get("customer_country")):
        errors.append("CUSTOMER_COUNTRY_REQUIRED")
    if not validate_required(row.get("customer_first_name")):
        errors.append("CUSTOMER_FIRST_NAME_REQUIRED")
    if not validate_int(row.get("customer_id")):
        errors.append("CUSTOMER_ID_INVALID")
    if not validate_required(row.get("customer_segment")):
        errors.append("CUSTOMER_SEGMENT_REQUIRED")
    if not validate_required(row.get("customer_state")):
        errors.append("CUSTOMER_STATE_REQUIRED")
    if not validate_required(row.get("customer_street")):
        errors.append("CUSTOMER_STREET_REQUIRED")
    if not validate_int(row.get("department_id")):
        errors.append("DEPARTMENT_ID_INVALID")
    if not validate_required(row.get("department_name")):
        errors.append("DEPARTMENT_NAME_REQUIRED")
    if not validate_latitude(row.get("latitude")):
        errors.append("LATITUDE_INVALID")
    if not validate_longitude(row.get("longitude")):
        errors.append("LONGITUDE_INVALID")
    if not validate_required(row.get("market")):
        errors.append("MARKET_REQUIRED")
    if not validate_required(row.get("order_city")):
        errors.append("ORDER_CITY_REQUIRED")
    if not validate_required(row.get("order_country")):
        errors.append("ORDER_COUNTRY_REQUIRED")
    if not validate_int(row.get("order_customer_id")):
        errors.append("ORDER_CUSTOMER_ID_INVALID")
    if validate_required(row.get("customer_id")) and validate_required(row.get("order_customer_id")):
        if str(row.get("customer_id")).strip() != str(row.get("order_customer_id")).strip():
            errors.append("CUSTOMER_ID_MISMATCH")
    if not validate_datetime(row.get("order_date")):
        errors.append("ORDER_DATE_INVALID")
    if not validate_int(row.get("order_id")):
        errors.append("ORDER_ID_INVALID")
    if not validate_int(row.get("order_item_cardprod_id")):
        errors.append("ORDER_ITEM_CARDPROD_ID_INVALID")
    if not validate_float(row.get("order_item_discount")):
        errors.append("ORDER_ITEM_DISCOUNT_INVALID")
    if not validate_float(row.get("order_item_discount_rate")):
        errors.append("ORDER_ITEM_DISCOUNT_RATE_INVALID")
    if not validate_int(row.get("order_item_id")):
        errors.append("ORDER_ITEM_ID_INVALID")
    if not validate_float(row.get("order_item_product_price")):
        errors.append("ORDER_ITEM_PRODUCT_PRICE_INVALID")
    if not validate_float(row.get("order_item_profit_ratio")):
        errors.append("ORDER_ITEM_PROFIT_RATIO_INVALID")
    if not validate_int(row.get("order_item_quantity")):
        errors.append("ORDER_ITEM_QUANTITY_INVALID")
    if not validate_float(row.get("sales")):
        errors.append("SALES_INVALID")
    if not validate_float(row.get("order_item_total")):
        errors.append("ORDER_ITEM_TOTAL_INVALID")
    if not validate_float(row.get("order_profit_per_order")):
        errors.append("ORDER_PROFIT_PER_ORDER_INVALID")
    if not validate_required(row.get("order_region")):
        errors.append("ORDER_REGION_REQUIRED")
    if not validate_required(row.get("order_state")):
        errors.append("ORDER_STATE_REQUIRED")
    if not validate_required(row.get("order_status")):
        errors.append("ORDER_STATUS_REQUIRED")
    if row.get("order_zipcode") and not validate_int(row.get("order_zipcode"), required=False):
        errors.append("ORDER_ZIPCODE_INVALID")
    if not validate_int(row.get("product_card_id")):
        errors.append("PRODUCT_CARD_ID_INVALID")
    if not validate_int(row.get("product_category_id")):
        errors.append("PRODUCT_CATEGORY_ID_INVALID")
    if not validate_required(row.get("product_image")):
        errors.append("PRODUCT_IMAGE_REQUIRED")
    if not validate_required(row.get("product_name")):
        errors.append("PRODUCT_NAME_REQUIRED")
    if not validate_float(row.get("product_price")):
        errors.append("PRODUCT_PRICE_INVALID")
    if not validate_int(row.get("product_status")):
        errors.append("PRODUCT_STATUS_INVALID")
    if not validate_datetime(row.get("shipping_date")):
        errors.append("SHIPPING_DATE_INVALID")
    if not validate_required(row.get("shipping_mode")):
        errors.append("SHIPPING_MODE_REQUIRED")

    return ValidationResult(is_valid=not errors, errors=errors)
