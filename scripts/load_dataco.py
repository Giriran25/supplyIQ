from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, select, update, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from scripts.etl.audit import (
    create_etl_job,
    ensure_etl_tables,
    record_etl_error,
    update_etl_job,
)
from scripts.etl.cleaners import clean_row
from scripts.etl.config import settings
from scripts.etl.loaders import (
    batch_rows,
    filter_by_parent_key,
    load_categories,
    load_customers,
    load_departments,
    load_order_items,
    load_orders,
    load_products,
    load_shipments,
)
from scripts.etl.transformers import aggregate_transforms
from scripts.etl.utils import (
    build_staging_record,
    normalize_header_names,
    read_csv_chunks,
    setup_logger,
)
from scripts.etl.validators import validate_row

logger = setup_logger("dataco_etl", settings.log_level)


def get_engine() -> Engine:
    return create_engine(settings.database_url, future=True)


def validate_input_file() -> Path:
    csv_path = settings.data_file_path
    if not csv_path.exists():
        raise FileNotFoundError(f"ETL source file not found: {csv_path}")
    return csv_path


def landing_phase(engine: Engine, job_id: str) -> None:
    staging = ensure_etl_tables(engine)[0]
    total_attempted = 0
    logger.info("Starting landing phase from %s", settings.data_file_path)

    with engine.begin() as connection:
        for chunk_index, chunk in enumerate(read_csv_chunks(settings.data_file_path, settings.chunk_size)):
            chunk = normalize_header_names(chunk)
            batch: list[dict[str, Any]] = []
            row_offset = chunk_index * settings.chunk_size

            for local_index, record in enumerate(chunk.to_dict(orient="records")):
                row_number = row_offset + local_index + 1
                batch.append(build_staging_record(record, row_number, settings.data_file_path.name))
                if len(batch) >= settings.batch_size:
                    _insert_staging_batch(connection, staging, batch)
                    total_attempted += len(batch)
                    batch.clear()

            if batch:
                _insert_staging_batch(connection, staging, batch)
                total_attempted += len(batch)

    logger.info("Landing phase attempted %s rows", total_attempted)
    with Session(engine) as session:
        update_etl_job(session, job_id, rows_staged=total_attempted)


def _insert_staging_batch(connection, staging, rows: list[dict[str, Any]]) -> None:
    stmt = pg_insert(staging).values(rows)
    stmt = stmt.on_conflict_do_nothing(index_elements=[staging.c.row_hash])
    connection.execute(stmt)


def validate_phase(engine: Engine, job_id: str) -> None:
    staging = ensure_etl_tables(engine)[0]
    validated = 0
    rejected = 0

    logger.info("Starting validation phase")
    with Session(engine) as session:
        query = select(staging).where(staging.c.validated == False)
        results = session.execute(query).all()

        for row in results:
            record = dict(row._mapping)
            validation = validate_row(record)
            if validation.is_valid:
                session.execute(
                    update(staging)
                    .where(staging.c.id == record["id"])
                    .values(validated=True, validation_errors=None)
                )
                validated += 1
            else:
                session.execute(
                    update(staging)
                    .where(staging.c.id == record["id"])
                    .values(validated=False, validation_errors=", ".join(validation.errors))
                )
                record_etl_error(
                    session=session,
                    job_id=job_id,
                    stage="VALIDATION",
                    row_number=record.get("source_row_number"),
                    error_code="VALIDATION_FAILED",
                    error_message=json.dumps(validation.errors),
                    target_table="staging_dataco",
                    source_payload=record,
                )
                rejected += 1

        session.commit()

    logger.info("Validation phase completed: %s valid, %s rejected", validated, rejected)
    with Session(engine) as session:
        update_etl_job(
            session,
            job_id,
            rows_validated=validated,
            rows_rejected=rejected,
        )


def _authenticated_staging_rows(engine: Engine) -> list[dict[str, Any]]:
    staging = ensure_etl_tables(engine)[0]
    rows: list[dict[str, Any]] = []
    with Session(engine) as session:
        query = select(staging).where(staging.c.validated == True)
        for row in session.execute(query):
            rows.append(dict(row._mapping))
    return rows


def transform_phase(engine: Engine, job_id: str) -> dict[str, list[dict[str, Any]]]:
    logger.info("Starting transform phase")
    cleaned_rows: list[dict[str, Any]] = []
    staging = ensure_etl_tables(engine)[0]

    with Session(engine) as session:
        query = select(staging).where(staging.c.validated == True)
        for row_index, row in enumerate(session.execute(query), start=1):
            cleaned_rows.append(clean_row(dict(row._mapping)))
            if row_index % settings.batch_size == 0:
                logger.debug("Transformed %s validated rows", row_index)

    payloads = aggregate_transforms(cleaned_rows)
    logger.info(
        "Transform phase produced: %s categories, %s departments, %s customers, %s products, %s orders, %s order_items, %s shipments",
        len(payloads["categories"]),
        len(payloads["departments"]),
        len(payloads["customers"]),
        len(payloads["products"]),
        len(payloads["orders"]),
        len(payloads["order_items"]),
        len(payloads["shipments"]),
    )
    return payloads


def load_phase(engine: Engine, job_id: str, payloads: dict[str, list[dict[str, Any]]]) -> None:
    logger.info("Starting load phase")
    total_loaded = 0

    with Session(engine) as session:
        categories = payloads["categories"]
        loaded = load_categories(session, engine, categories, job_id)
        total_loaded += loaded
        session.commit()

        departments = payloads["departments"]
        loaded = load_departments(session, engine, departments, job_id)
        total_loaded += loaded
        session.commit()

        customers = payloads["customers"]
        loaded = load_customers(session, engine, customers, job_id)
        total_loaded += loaded
        session.commit()

        products = filter_by_parent_key(
            session=session,
            rows=payloads["products"],
            fk_column="category_id",
            parent_table_name="categories",
            job_id=job_id,
            stage="LOAD_PRODUCTS",
            target_table="products",
        )
        products = filter_by_parent_key(
            session=session,
            rows=products,
            fk_column="department_id",
            parent_table_name="departments",
            job_id=job_id,
            stage="LOAD_PRODUCTS",
            target_table="products",
        )
        loaded = load_products(session, engine, products, job_id)
        total_loaded += loaded
        session.commit()

        orders = filter_by_parent_key(
            session=session,
            rows=payloads["orders"],
            fk_column="customer_id",
            parent_table_name="customers",
            job_id=job_id,
            stage="LOAD_ORDERS",
            target_table="orders",
        )
        loaded = load_orders(session, engine, orders, job_id)
        total_loaded += loaded
        session.commit()

        items = filter_by_parent_key(
            session=session,
            rows=payloads["order_items"],
            fk_column="order_id",
            parent_table_name="orders",
            job_id=job_id,
            stage="LOAD_ORDER_ITEMS",
            target_table="order_items",
        )
        items = filter_by_parent_key(
            session=session,
            rows=items,
            fk_column="product_id",
            parent_table_name="products",
            job_id=job_id,
            stage="LOAD_ORDER_ITEMS",
            target_table="order_items",
        )
        for batch in batch_rows(items, settings.batch_size):
            loaded = load_order_items(session, engine, batch, job_id)
            total_loaded += loaded
            session.commit()

        shipments = filter_by_parent_key(
            session=session,
            rows=payloads["shipments"],
            fk_column="order_id",
            parent_table_name="orders",
            job_id=job_id,
            stage="LOAD_SHIPMENTS",
            target_table="shipments",
        )
        for batch in batch_rows(shipments, settings.batch_size):
            loaded = load_shipments(session, engine, batch, job_id)
            total_loaded += loaded
            session.commit()

        update_etl_job(session, job_id, rows_loaded=total_loaded)

    logger.info("Load phase completed, total loaded rows: %s", total_loaded)


def post_load_validation(engine: Engine, job_id: str, payloads: dict[str, list[dict[str, Any]]]) -> None:
    logger.info("Starting post-load validation")
    table_names = [
        "categories",
        "departments",
        "customers",
        "products",
        "orders",
        "order_items",
        "shipments",
    ]
    with Session(engine) as session:
        counts = {name: _count_table(session, name) for name in table_names}
        logger.info("Current counts: %s", counts)
        expected = {
            "categories": len(payloads["categories"]),
            "departments": len(payloads["departments"]),
            "customers": len(payloads["customers"]),
            "products": len(payloads["products"]),
            "orders": len(payloads["orders"]),
            "order_items": len(payloads["order_items"]),
            "shipments": len(payloads["shipments"]),
        }

        mismatches = [
            f"{name}: expected {expected[name]}, actual {counts[name]}"
            for name in table_names
            if counts[name] < expected[name]
        ]

        if mismatches:
            logger.warning("Post-load validation mismatch detected: %s", "; ".join(mismatches))
            update_etl_job(session, job_id, error_summary="; ".join(mismatches), job_status="COMPLETED")
        else:
            logger.info("Post-load validation passed for all target tables")
            update_etl_job(session, job_id, job_status="COMPLETED")


def _count_table(session: Session, table_name: str) -> int:
    from scripts.etl.loaders import reflect_table

    table = reflect_table(session.bind, table_name)
    result = session.execute(select(func.count()).select_from(table)).scalar_one()
    return int(result)


def main() -> int:
    validate_input_file()
    engine = get_engine()
    ensure_etl_tables(engine)

    with Session(engine) as session:
        job_id = create_etl_job(session, settings.job_name, str(settings.data_file_path.name))

    try:
        landing_phase(engine, job_id)
        validate_phase(engine, job_id)
        payloads = transform_phase(engine, job_id)
        load_phase(engine, job_id, payloads)
        post_load_validation(engine, job_id, payloads)

        logger.info("ETL job %s completed successfully", job_id)
        return 0
    except Exception as exc:
        logger.exception("ETL job failed")
        with Session(engine) as session:
            update_etl_job(session, job_id, job_status="FAILED", error_summary=str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
