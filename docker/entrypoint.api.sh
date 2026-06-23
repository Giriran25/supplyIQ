#!/usr/bin/env sh
set -e

# Simple entrypoint: run migrations then start uvicorn
if [ -z "$DATABASE_URL" ]; then
  echo "DATABASE_URL not set"
  exit 1
fi

alembic upgrade head

# Seed DB only in development
if [ "$ENV" = "development" ]; then
  python scripts/seed_db.py
fi

exec uvicorn app.api.main:app --host 0.0.0.0 --port ${API_PORT:-8000} --reload
