from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


# Construct database URL from settings
DATABASE_URL = (
    f"postgresql+psycopg://{settings.postgres_user}:"
    f"{settings.postgres_password}@{settings.postgres_host}:"
    f"{settings.postgres_port}/{settings.postgres_db}"
)

# Create engine with pool configuration for production
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)


def get_db():
    """Dependency injection for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
