from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Iterable

from .cleaners import clean_masked_pii, clean_string, clean_zipcode, normalize_enum, parse_timestamp, to_boolean, to_decimal, to_int


def transform_category(row: dict[str, object]) -> dict[str, object]:
    category_id = to_int(row["category_id"])
    return {
        "id": category_id,
        "external_category_id": category_id,
        "name": clean_string(row["category_name"]),
    }


def transform_department(row: dict[str, object]) -> dict[str, object]:
    department_id = to_int(row["department_id"])
    return {
        "id": department_id,
        "external_department_id": department_id,
        "name": clean_string(row["department_name"]),
    }


def transform_customer(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": to_int(row["customer_id"]),
        "first_name": clean_string(row["customer_first_name"]),
        "last_name": clean_string(row["customer_last_name"]) or "UNKNOWN",
        "email": clean_masked_pii(row["customer_email"]),
        "password_hash": clean_masked_pii(row["customer_password"]),
        "segment": normalize_enum(row["customer_segment"]),
        "address_line1": clean_string(row["customer_street"]),
        "city": clean_string(row["customer_city"]),
        "state": normalize_enum(row["customer_state"]),
        "country": normalize_enum(row["customer_country"]),
        "zipcode": clean_zipcode(row["customer_zipcode"]),
        "latitude": float(row["latitude"]),
        "longitude": float(row["longitude"]),
    }


def transform_product(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": to_int(row["product_card_id"]),
        "name": clean_string(row["product_name"]),
        "description": clean_string(row["product_description"]),
        "image_url": clean_string(row["product_image"]),
        "price": to_decimal(row["product_price"]),
        "status_code": to_int(row["product_status"]),
        "category_id": to_int(row["category_id"]),
        "department_id": to_int(row["department_id"]),
    }


def transform_order(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": to_int(row["order_id"]),
        "customer_id": to_int(row["order_customer_id"]),
        "order_date": parse_timestamp(row["order_date"]),
        "status": normalize_enum(row["order_status"]),
        "region": normalize_enum(row["order_region"]),
        "state": normalize_enum(row["order_state"]),
        "market": normalize_enum(row["market"]),
        "ship_city": clean_string(row["order_city"]),
        "ship_country": normalize_enum(row["order_country"]),
        "zipcode": clean_zipcode(row["order_zipcode"]),
        "payment_type": normalize_enum(row["source_type"]),
        "sales_total": to_decimal(row["sales"]),
        "profit_amount": to_decimal(row["order_profit_per_order"]),
        "benefit": to_decimal(row["benefit_per_order"]),
        "sales_per_customer": to_decimal(row["sales_per_customer"]),
    }


def transform_order_item(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": to_int(row["order_item_id"]),
        "order_id": to_int(row["order_id"]),
        "product_id": to_int(row["order_item_cardprod_id"]),
        "quantity": to_int(row["order_item_quantity"]),
        "unit_price": to_decimal(row["order_item_product_price"]),
        "discount_amount": to_decimal(row["order_item_discount"]),
        "discount_rate": to_decimal(row["order_item_discount_rate"]),
        "line_total": to_decimal(row["order_item_total"]),
        "profit_ratio": to_decimal(row["order_item_profit_ratio"]),
    }


def transform_shipment(row: dict[str, object]) -> dict[str, object]:
    return {
        "id": to_int(row["order_id"]),
        "order_id": to_int(row["order_id"]),
        "shipped_at": parse_timestamp(row["shipping_date"]),
        "planned_transit_days": to_int(row["days_for_shipment_scheduled"]),
        "actual_transit_days": to_int(row["days_for_shipping_real"]),
        "delivery_status": normalize_enum(row["delivery_status"]),
        "late_delivery_risk": to_boolean(row["late_delivery_risk"]),
        "shipping_mode": normalize_enum(row["shipping_mode"]),
    }


def aggregate_transforms(rows: Iterable[dict[str, object]]) -> dict[str, list[dict[str, object]]]:
    categories: dict[int, dict[str, object]] = {}
    departments: dict[int, dict[str, object]] = {}
    customers: dict[int, dict[str, object]] = {}
    products: dict[int, dict[str, object]] = {}
    orders: dict[int, dict[str, object]] = {}
    shipments: dict[int, dict[str, object]] = {}
    order_items: list[dict[str, object]] = []

    for raw in rows:
        category = transform_category(raw)
        categories[category["id"]] = category

        department = transform_department(raw)
        departments[department["id"]] = department

        customer = transform_customer(raw)
        customers[customer["id"]] = customer

        product = transform_product(raw)
        products[product["id"]] = product

        order_item = transform_order_item(raw)
        order_items.append(order_item)

        order_id = order_item["order_id"]
        if order_id not in orders:
            orders[order_id] = transform_order(raw)
            orders[order_id]["sales_total"] = Decimal("0.00")

        if order_item["line_total"] is not None:
            orders[order_id]["sales_total"] += order_item["line_total"]

        if shipments.get(order_id) is None:
            shipments[order_id] = transform_shipment(raw)

    return {
        "categories": list(categories.values()),
        "departments": list(departments.values()),
        "customers": list(customers.values()),
        "products": list(products.values()),
        "orders": list(orders.values()),
        "order_items": order_items,
        "shipments": list(shipments.values()),
    }
