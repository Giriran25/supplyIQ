from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd


SOURCE_HEADER_MAP = {
    "Type": "source_type",
    "Days for shipping (real)": "days_for_shipping_real",
    "Days for shipment (scheduled)": "days_for_shipment_scheduled",
    "Benefit per order": "benefit_per_order",
    "Sales per customer": "sales_per_customer",
    "Delivery Status": "delivery_status",
    "Late_delivery_risk": "late_delivery_risk",
    "Category Id": "category_id",
    "Category Name": "category_name",
    "Customer City": "customer_city",
    "Customer Country": "customer_country",
    "Customer Email": "customer_email",
    "Customer Fname": "customer_first_name",
    "Customer Id": "customer_id",
    "Customer Lname": "customer_last_name",
    "Customer Password": "customer_password",
    "Customer Segment": "customer_segment",
    "Customer State": "customer_state",
    "Customer Street": "customer_street",
    "Customer Zipcode": "customer_zipcode",
    "Department Id": "department_id",
    "Department Name": "department_name",
    "Latitude": "latitude",
    "Longitude": "longitude",
    "Market": "market",
    "Order City": "order_city",
    "Order Country": "order_country",
    "Order Customer Id": "order_customer_id",
    "order date (DateOrders)": "order_date",
    "Order Id": "order_id",
    "Order Item Cardprod Id": "order_item_cardprod_id",
    "Order Item Discount": "order_item_discount",
    "Order Item Discount Rate": "order_item_discount_rate",
    "Order Item Id": "order_item_id",
    "Order Item Product Price": "order_item_product_price",
    "Order Item Profit Ratio": "order_item_profit_ratio",
    "Order Item Quantity": "order_item_quantity",
    "Sales": "sales",
    "Order Item Total": "order_item_total",
    "Order Profit Per Order": "order_profit_per_order",
    "Order Region": "order_region",
    "Order State": "order_state",
    "Order Status": "order_status",
    "Order Zipcode": "order_zipcode",
    "Product Card Id": "product_card_id",
    "Product Category Id": "product_category_id",
    "Product Description": "product_description",
    "Product Image": "product_image",
    "Product Name": "product_name",
    "Product Price": "product_price",
    "Product Status": "product_status",
    "shipping date (DateOrders)": "shipping_date",
    "Shipping Mode": "shipping_mode",
}

SOURCE_COLUMNS = list(SOURCE_HEADER_MAP.keys())
STAGING_COLUMNS = list(SOURCE_HEADER_MAP.values())


def setup_logger(name: str, level: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    handler = logging.StreamHandler()
    handler.setLevel(level.upper())
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger


def compute_row_hash(values: dict[str, Any]) -> str:
    serial = json.dumps(values, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(serial.encode("utf-8")).hexdigest()


def normalize_header_names(frame: pd.DataFrame) -> pd.DataFrame:
    available = [header for header in frame.columns if header in SOURCE_HEADER_MAP]
    rename_map = {header: SOURCE_HEADER_MAP[header] for header in available}
    return frame.rename(columns=rename_map)


def read_csv_chunks(csv_path: Path, chunk_size: int):
    return pd.read_csv(
        csv_path,
        dtype=str,
        keep_default_na=False,
        na_filter=False,
        chunksize=chunk_size,
        encoding="latin1",
    )


def build_staging_record(row: dict[str, Any], row_number: int, source_file: str) -> dict[str, Any]:
    row_values = {safe_name: row.get(safe_name, "") for safe_name in STAGING_COLUMNS}
    row_values["source_row_number"] = row_number
    row_values["source_file_name"] = source_file
    row_values["row_hash"] = compute_row_hash(row_values)
    row_values["validated"] = False
    row_values["validation_errors"] = None
    return row_values
