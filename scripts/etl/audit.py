from __future__ import annotations

import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.engine import Engine

from .utils import STAGING_COLUMNS

metadata = MetaData()


def create_staging_table() -> Table:
    columns = [
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("source_row_number", Integer, nullable=False),
        Column("source_file_name", Text, nullable=False),
        Column("row_hash", String(64), nullable=False, unique=True),
        Column("validated", Boolean, nullable=False, server_default=text("FALSE")),
        Column("validation_errors", Text, nullable=True),
    ]

    for column_name in STAGING_COLUMNS:
        columns.append(Column(column_name, Text, nullable=True))

    columns.extend(
        [
            Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
            Column(
                "updated_at",
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),
                nullable=False,
            ),
        ]
    )

    return Table("staging_dataco", metadata, *columns)


def create_etl_jobs_table() -> Table:
    return Table(
        "etl_jobs",
        metadata,
        Column("job_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column("job_name", String(100), nullable=False),
        Column("source_file", Text, nullable=False),
        Column("job_status", String(50), nullable=False, server_default=text("'RUNNING'")),
        Column("rows_staged", Integer, nullable=False, default=0),
        Column("rows_validated", Integer, nullable=False, default=0),
        Column("rows_rejected", Integer, nullable=False, default=0),
        Column("rows_loaded", Integer, nullable=False, default=0),
        Column("error_summary", Text, nullable=True),
        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
        Column(
            "updated_at",
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        ),
    )


def create_etl_errors_table() -> Table:
    return Table(
        "etl_errors",
        metadata,
        Column("error_id", UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        Column("job_id", UUID(as_uuid=True), ForeignKey("etl_jobs.job_id", ondelete="CASCADE"), nullable=False),
        Column("stage", String(50), nullable=False),
        Column("row_number", Integer, nullable=True),
        Column("error_code", String(100), nullable=False),
        Column("error_message", Text, nullable=False),
        Column("target_table", String(100), nullable=True),
        Column("source_payload", JSONB, nullable=True),
        Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
    )


from sqlalchemy import insert


def ensure_etl_tables(engine: Engine) -> tuple[Table, Table, Table]:
    staging = create_staging_table()
    jobs = create_etl_jobs_table()
    errors = create_etl_errors_table()
    metadata.create_all(engine, tables=[staging, jobs, errors])
    return staging, jobs, errors


def create_etl_job(session, job_name: str, source_file: str):
    job_id = uuid.uuid4()
    stmt = insert(create_etl_jobs_table()).values(
        job_id=job_id,
        job_name=job_name,
        source_file=source_file,
        job_status="RUNNING",
        rows_staged=0,
        rows_validated=0,
        rows_rejected=0,
        rows_loaded=0,
        error_summary=None,
    )
    session.execute(stmt)
    session.commit()
    return job_id


def update_etl_job(session, job_id, **values):
    jobs_table = create_etl_jobs_table()
    stmt = jobs_table.update().where(jobs_table.c.job_id == job_id).values(**values)
    session.execute(stmt)
    session.commit()


def record_etl_error(
    session,
    job_id,
    stage: str,
    row_number: int | None,
    error_code: str,
    error_message: str,
    target_table: str | None = None,
    source_payload: dict | None = None,
):
    errors_table = create_etl_errors_table()
    payload = source_payload if source_payload is not None else {}
    stmt = insert(errors_table).values(
        error_id=uuid.uuid4(),
        job_id=job_id,
        stage=stage,
        row_number=row_number,
        error_code=error_code,
        error_message=error_message,
        target_table=target_table,
        source_payload=payload,
    )
    session.execute(stmt)
    session.flush()
