from __future__ import annotations

from typing import Iterable

from sqlalchemy import MetaData, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .audit import record_etl_error, update_etl_job


def reflect_table(engine: Engine, table_name: str):
    metadata = MetaData()
    metadata.reflect(bind=engine, only=[table_name])
    return metadata.tables[table_name]


def upsert_rows(
    session: Session,
    table,
    rows: list[dict[str, object]],
    conflict_columns: list[str],
    update_columns: list[str],
    job_id: str,
    stage: str,
    target_table: str,
) -> int:
    if not rows:
        return 0

    total_loaded = 0
    batch_size = 1000

    try:
        for batch in batch_rows(rows, batch_size):
            stmt = pg_insert(table).values(batch)
            update_values = {col: getattr(stmt.excluded, col) for col in update_columns}
            stmt = stmt.on_conflict_do_update(index_elements=conflict_columns, set_=update_values)
            session.execute(stmt)
            session.flush()
            total_loaded += len(batch)
        return total_loaded
    except IntegrityError as exc:
        session.rollback()
        for row in rows:
            record_etl_error(
                session=session,
                job_id=job_id,
                stage=stage,
                row_number=row.get("source_row_number"),
                error_code="LOAD_INTEGRITY_ERROR",
                error_message=str(exc.__context__ or exc),
                target_table=target_table,
                source_payload=row,
            )
        raise


def fetch_existing_ids(session: Session, table_name: str, ids: set[int]) -> set[int]:
    """
    Fetch existing primary keys from a table in batches to avoid generating
    extremely large SQL IN (...) clauses that exceed PostgreSQL/SQLAlchemy
    parameter limits.
    """
    if not ids:
        return set()

    table = reflect_table(session.bind, table_name)

    existing_ids: set[int] = set()
    batch_size = 1000

    ids_list = list(ids)

    for start in range(0, len(ids_list), batch_size):
        batch = ids_list[start:start + batch_size]

        result = session.execute(
            select(table.c.id).where(table.c.id.in_(batch))
        )

        existing_ids.update(row[0] for row in result.fetchall())

    return existing_ids


def filter_by_parent_key(
    session: Session,
    rows: list[dict[str, object]],
    fk_column: str,
    parent_table_name: str,
    job_id: str,
    stage: str,
    target_table: str,
) -> list[dict[str, object]]:
    parent_ids = {row[fk_column] for row in rows if row.get(fk_column) is not None}
    existing = fetch_existing_ids(session, parent_table_name, parent_ids)
    valid_rows = []
    for row in rows:
        parent_id = row.get(fk_column)
        if parent_id is None or parent_id in existing:
            valid_rows.append(row)
            continue

        record_etl_error(
            session=session,
            job_id=job_id,
            stage=stage,
            row_number=row.get("source_row_number"),
            error_code=f"FK_{fk_column.upper()}_MISSING",
            error_message=f"Missing parent {parent_table_name}.id={parent_id}",
            target_table=target_table,
            source_payload=row,
        )
    return valid_rows


def load_categories(session: Session, engine: Engine, rows: list[dict[str, object]], job_id: str) -> int:
    table = reflect_table(engine, "categories")
    return upsert_rows(
        session,
        table,
        rows,
        conflict_columns=["id"],
        update_columns=["name", "external_category_id"],
        job_id=job_id,
        stage="LOAD_CATEGORIES",
        target_table="categories",
    )


def load_departments(session: Session, engine: Engine, rows: list[dict[str, object]], job_id: str) -> int:
    table = reflect_table(engine, "departments")
    return upsert_rows(
        session,
        table,
        rows,
        conflict_columns=["id"],
        update_columns=["name", "external_department_id"],
        job_id=job_id,
        stage="LOAD_DEPARTMENTS",
        target_table="departments",
    )


def load_customers(session: Session, engine: Engine, rows: list[dict[str, object]], job_id: str) -> int:
    table = reflect_table(engine, "customers")
    normalized_rows = [
        {
            **row,
            "last_name": row.get("last_name") or "UNKNOWN",
        }
        for row in rows
    ]
    return upsert_rows(
        session,
        table,
        normalized_rows,
        conflict_columns=["id"],
        update_columns=[
            "first_name",
            "last_name",
            "email",
            "password_hash",
            "segment",
            "address_line1",
            "city",
            "state",
            "country",
            "zipcode",
            "latitude",
            "longitude",
        ],
        job_id=job_id,
        stage="LOAD_CUSTOMERS",
        target_table="customers",
    )


def load_products(session: Session, engine: Engine, rows: list[dict[str, object]], job_id: str) -> int:
    table = reflect_table(engine, "products")
    return upsert_rows(
        session,
        table,
        rows,
        conflict_columns=["id"],
        update_columns=[
            "name",
            "description",
            "image_url",
            "price",
            "status_code",
            "category_id",
            "department_id",
        ],
        job_id=job_id,
        stage="LOAD_PRODUCTS",
        target_table="products",
    )


def load_orders(session: Session, engine: Engine, rows: list[dict[str, object]], job_id: str) -> int:
    table = reflect_table(engine, "orders")
    return upsert_rows(
        session,
        table,
        rows,
        conflict_columns=["id"],
        update_columns=[
            "customer_id",
            "order_date",
            "status",
            "region",
            "state",
            "market",
            "ship_city",
            "ship_country",
            "zipcode",
            "payment_type",
            "sales_total",
            "profit_amount",
            "benefit",
            "sales_per_customer",
        ],
        job_id=job_id,
        stage="LOAD_ORDERS",
        target_table="orders",
    )


def load_order_items(session: Session, engine: Engine, rows: list[dict[str, object]], job_id: str) -> int:
    table = reflect_table(engine, "order_items")
    return upsert_rows(
        session,
        table,
        rows,
        conflict_columns=["id"],
        update_columns=[
            "order_id",
            "product_id",
            "quantity",
            "unit_price",
            "discount_amount",
            "discount_rate",
            "line_total",
            "profit_ratio",
        ],
        job_id=job_id,
        stage="LOAD_ORDER_ITEMS",
        target_table="order_items",
    )


def load_shipments(session: Session, engine: Engine, rows: list[dict[str, object]], job_id: str) -> int:
    table = reflect_table(engine, "shipments")
    return upsert_rows(
        session,
        table,
        rows,
        conflict_columns=["id"],
        update_columns=[
            "order_id",
            "shipped_at",
            "planned_transit_days",
            "actual_transit_days",
            "delivery_status",
            "late_delivery_risk",
            "shipping_mode",
        ],
        job_id=job_id,
        stage="LOAD_SHIPMENTS",
        target_table="shipments",
    )


def batch_rows(rows: list[dict[str, object]], batch_size: int) -> Iterable[list[dict[str, object]]]:
    for index in range(0, len(rows), batch_size):
        yield rows[index : index + batch_size]
