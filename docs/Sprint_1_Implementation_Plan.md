# SupplyChainIQ: Sprint 1 Implementation Plan
## Foundation Layer — Production-Grade Setup (2 weeks)

---

## EXECUTIVE SUMMARY

**Sprint 1 Goal:** Build the foundational layer of SupplyChainIQ — repository structure, Docker environment, database schema, SQLAlchemy models, data pipeline, and FastAPI skeleton.

**Outcome:** A clean, production-ready codebase with fully functional database layer, synthetic data generation, ETL pipeline, and health/analytics API endpoints. Ready for Sprint 2 (ML models and business logic).

**Timeline:** 10 business days (2 weeks)

**Team:** 1 Staff Engineer (full-time)

---

## PART I: COMPLETE FILE TREE (Final State, End of Sprint 1)

```
SupplyChainIQ/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml (placeholder for future CI/CD)
│
├── .vscode/
│   ├── launch.json (debug config)
│   ├── settings.json (Python formatting)
│
├── alembic/
│   ├── versions/
│   │   ├── 001_initial_schema.py (first migration)
│   ├── env.py (migration environment config)
│   ├── script.py.mako (migration template)
│   ├── alembic.ini (Alembic configuration)
│
├── app/
│   ├── __init__.py (package marker)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py (Pydantic BaseSettings, environment vars)
│   │   ├── database.py (SQLAlchemy engine, session factory)
│   │   ├── logging.py (structured logging config)
│   │   ├── constants.py (static values, thresholds)
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py (DeclarativeBase, TimestampMixin)
│   │   ├── supplier.py (Supplier, SupplierRiskScore models)
│   │   ├── order.py (Order model)
│   │   ├── shipment.py (Shipment, ShipmentTracking models)
│   │   ├── product.py (Product model)
│   │   ├── inventory.py (Inventory, InventorySnapshot models)
│   │   ├── warehouse.py (Warehouse model)
│   │   ├── risk_score.py (RiskScore, SCRIScore models)
│   │   ├── simulation.py (SimulationRun, SimulationResult models)
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── base.py (BaseSchema, TimestampSchema mixins)
│   │   ├── supplier.py (SupplierSchema, SupplierDetailSchema)
│   │   ├── shipment.py (ShipmentSchema, ShipmentDetailSchema)
│   │   ├── analytics.py (KPISchema, SupplierMetricsSchema)
│   │   ├── prediction.py (DelayPredictionInputSchema, DelayPredictionOutputSchema)
│   │   ├── risk.py (SupplierRiskSchema, RiskSummarySchema)
│   │   ├── resilience.py (SCRISchema, DriverBreakdownSchema)
│   │   ├── simulation.py (SimulationInputSchema, SimulationOutputSchema)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py (FastAPI app factory, middleware, exception handlers)
│   │   ├── health.py (health check router)
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── analytics.py (GET /api/analytics/kpis, /api/analytics/suppliers)
│   │   │   ├── data.py (POST /api/data/upload, GET /api/data/status)
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── etl.py (ETL pipeline, data validation, ingestion)
│   │   ├── analytics.py (KPI computation, aggregations)
│   │   ├── data_generator.py (synthetic data generation)
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py (database session dependency for FastAPI)
│   │   ├── crud.py (basic CRUD operations, query helpers)
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── errors.py (custom exceptions)
│   │   ├── validators.py (Pydantic validators)
│   │   ├── helpers.py (utility functions)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py (pytest fixtures, test DB setup)
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_config.py (test environment configuration)
│   │   ├── test_models.py (SQLAlchemy model validation)
│   │   ├── test_schemas.py (Pydantic schema validation)
│   │   ├── test_etl.py (ETL pipeline unit tests)
│   │   ├── test_analytics.py (KPI computation tests)
│   │   ├── test_data_generator.py (synthetic data generation tests)
│   │
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── test_api_health.py (health endpoint tests)
│   │   ├── test_api_analytics.py (analytics endpoint tests)
│   │   ├── test_database.py (database connection, migrations)
│   │
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── sample_data.py (reusable test data factories)
│
├── scripts/
│   ├── __init__.py
│   ├── seed_db.py (populate DB with synthetic data)
│   ├── reset_db.py (drop and recreate schema)
│   ├── migrate_db.py (run Alembic migrations)
│   ├── create_superuser.py (create admin user, deferred to Sprint 2)
│
├── docker/
│   ├── Dockerfile.api (FastAPI service)
│   ├── Dockerfile.streamlit (Streamlit service, minimal for Sprint 1)
│   ├── entrypoint.api.sh (API container entrypoint)
│   ├── entrypoint.streamlit.sh (Streamlit entrypoint)
│
├── logs/
│   ├── .gitkeep (logs directory)
│
├── data/
│   ├── .gitkeep
│   ├── raw/
│   │   ├── .gitkeep
│   ├── processed/
│   │   ├── .gitkeep
│
├── docs/
│   ├── SCRI_v2_Research_Design.md (existing)
│   ├── Implementation_Blueprint_MVP.md (existing)
│   ├── Sprint_1_Implementation_Plan.md (this document)
│   ├── API.md (API documentation, generated from FastAPI)
│   ├── DATABASE.md (database schema, entity relationships)
│   ├── SETUP.md (local dev setup, Docker commands)
│
├── .env.example (template for environment variables)
├── .env.local (local dev, not in repo; created by developer)
├── .env.test (test environment)
├── .env.docker (Docker environment)
│
├── .gitignore
├── .dockerignore
│
├── docker-compose.yml (PostgreSQL, FastAPI, Streamlit services)
├── docker-compose.override.yml (local dev overrides)
│
├── pyproject.toml (Python project metadata, dependencies, tools)
├── requirements.txt (pinned dependencies)
├── requirements-dev.txt (dev dependencies: pytest, black, ruff, etc.)
│
├── Makefile (convenience commands for common tasks)
├── README.md (project overview, quickstart)
├── CONTRIBUTING.md (development guidelines)
├── LICENSE
│
└── .python-version (pyenv/asdf, e.g., "3.11.0")
```

---

## PART II: IMPLEMENTATION ORDER (Step-by-Step)

### Phase 1: Project Setup (Days 1–2)

**Day 1 AM: Repository & Dependencies**
1. Initialize Git repo, clone/create structure
2. Create `pyproject.toml` with core dependencies:
   - FastAPI, Uvicorn
   - SQLAlchemy 2.0+
   - Psycopg2-binary (PostgreSQL adapter)
   - Pydantic v2
   - Alembic (migrations)
   - Python-dotenv (environment vars)
   - Loguru or structlog (structured logging)
   - Pytest, pytest-asyncio (testing)
   - Docker Python SDK (for integration tests)

3. Create `requirements.txt` (pinned versions) and `requirements-dev.txt`
4. Create `.gitignore`, `.dockerignore`
5. Set up `.python-version` (e.g., 3.11.0)

**Day 1 PM: Environment & Config**
1. Create `app/core/config.py`:
   - Pydantic BaseSettings for ENV variable loading
   - Define DATABASE_URL, DEBUG, LOG_LEVEL, OPENAI_API_KEY (stub), etc.
   - Support `.env` file loading via python-dotenv
   - Validate critical config at startup

2. Create `.env.example`:
   - Template with all required/optional vars
   - Comments explaining each var
   - Sample values (non-sensitive)

3. Create `.env.local` (developer's local copy, in .gitignore)
4. Create `.env.test` (test environment)
5. Create `.env.docker` (Docker Compose environment)

**Day 2 AM: Logging & Core Infrastructure**
1. Create `app/core/logging.py`:
   - Structured JSON logging (Loguru or structlog)
   - Log levels: DEBUG, INFO, WARNING, ERROR
   - Output to stdout + file
   - Request logging middleware setup

2. Create `app/core/constants.py`:
   - SCRI thresholds, weights
   - Risk score cutoffs
   - Pagination defaults
   - Feature engineering thresholds (e.g., rolling window lengths)

3. Create `app/utils/errors.py`:
   - Custom exception classes (DatabaseError, ValidationError, NotFoundError, etc.)
   - Exception handlers for FastAPI

4. Create `app/utils/validators.py`:
   - Pydantic validators (e.g., future dates, positive amounts)

**Day 2 PM: Database & Models Setup**
1. Create `app/core/database.py`:
   - SQLAlchemy engine setup
   - Session factory
   - get_db() dependency function for FastAPI
   - Connection pooling config

2. Create `app/models/base.py`:
   - Base declarative class
   - TimestampMixin (created_at, updated_at)
   - Reusable base fields

3. Create ALL model files (`supplier.py`, `order.py`, `shipment.py`, etc.):
   - SQLAlchemy ORM models
   - Type hints on all fields
   - Relationships (FK, backrefs)
   - Indexes on key columns

---

### Phase 2: Database & Migrations (Days 2–3)

**Day 3 AM: Database Schema**
1. Create `alembic/` directory structure (via `alembic init`)
2. Configure `alembic/alembic.ini` to use environment variables for DB connection
3. Create `alembic/env.py` with proper target_metadata setup
4. Create first migration: `alembic/versions/001_initial_schema.py`
   - All table creations (suppliers, orders, shipments, products, inventory, warehouses, risk_scores, simulations)
   - Foreign keys, constraints, indexes
   - Comment descriptions on tables/columns

5. Test migration:
   - `alembic upgrade head` successfully creates schema
   - Verify schema in PostgreSQL (psql or DBeaver)
   - Verify reverse migration works: `alembic downgrade -1`

**Day 3 PM: Pydantic Schemas**
1. Create `app/schemas/base.py`:
   - BaseSchema mixin
   - TimestampSchema (read-only created_at, updated_at)

2. Create all Pydantic schemas:
   - `schemas/supplier.py`: SupplierSchema (read), SupplierCreateSchema (write), SupplierDetailSchema (full detail)
   - `schemas/shipment.py`: ShipmentSchema (read), ShipmentDetailSchema
   - `schemas/analytics.py`: KPISchema, SupplierMetricsSchema, AnalyticsResponseSchema
   - `schemas/prediction.py`: DelayPredictionInputSchema, DelayPredictionOutputSchema (placeholder for Sprint 2)
   - `schemas/risk.py`: SupplierRiskSchema, RiskSummarySchema (placeholder for Sprint 2)
   - `schemas/resilience.py`: SCRISchema, DriverBreakdownSchema (placeholder for Sprint 2)
   - `schemas/simulation.py`: SimulationInputSchema, SimulationOutputSchema (placeholder for Sprint 2)

---

### Phase 3: Data Layer (Days 4–5)

**Day 4 AM: CRUD & Database Utilities**
1. Create `app/db/crud.py`:
   - Generic CRUD functions: create_record, read_record, read_by_id, update_record, delete_record
   - Query helpers: get_suppliers_by_risk, get_shipments_in_window, get_inventory_by_warehouse, etc.
   - Pagination helper

2. Create `app/db/session.py`:
   - get_db() dependency
   - Context managers for transactions

**Day 4 PM: Synthetic Data Generator**
1. Create `app/services/data_generator.py`:
   - Supplier generation (100 records with realistic fields: name, region, lead_time_mean, lead_time_std, on_time_rate, capacity_estimate)
   - Product generation (50 SKUs with category, unit_cost, unit_price, criticality)
   - Order generation (1,000 orders with dates, products, quantities, values, regions)
   - Shipment generation (5,000 records with lead times, actual delivery, delay flags)
   - Inventory generation (daily snapshots for products × warehouses)
   - Warehouse generation (5 warehouses in different regions)

2. Use Faker for realistic data (names, addresses, dates)
3. Use NumPy/SciPy for realistic distributions (LogNormal lead times, Bernoulli delays, seasonal demand)
4. Ensure referential integrity (shipments reference valid supplier/product/order)

**Day 5 AM: ETL Pipeline**
1. Create `app/services/etl.py`:
   - CSV ingestion: read, parse, validate schema
   - Data validation: type checking, constraint validation, bounds checking
   - Data cleansing: handle NULLs, duplicates, outliers (with logging)
   - Staging: insert into temporary tables or mark as "staging" records
   - Persistence: batch insert into main tables with transaction management
   - Logging: detailed progress logging (rows read, validated, inserted, errors)
   - Error handling: collect validation errors, roll back on critical failures

2. Create `app/services/analytics.py`:
   - KPI computation functions:
     - compute_revenue_kpi(date_range) → YTD revenue, MoM %, targets
     - compute_order_kpi() → order counts, status breakdown
     - compute_delay_kpi() → delay rate, avg delay days, by supplier/region
     - compute_otif_kpi() → on-time in-full rate
     - compute_lead_time_kpi() → avg, std, p95
   - Supplier metrics:
     - get_top_suppliers_by_risk() → ranked by performance
     - get_supplier_performance(supplier_id) → detailed metrics
   - All functions query database, aggregate, return AnalyticsSchema

**Day 5 PM: Seed & Reset Scripts**
1. Create `scripts/seed_db.py`:
   - Drop and recreate schema
   - Run migrations
   - Generate synthetic data
   - Insert into database
   - Verify row counts
   - Log summary

2. Create `scripts/reset_db.py`:
   - Downgrade all migrations
   - Drop database (optional: create fresh)
   - Optionally re-seed

3. Create `scripts/migrate_db.py`:
   - Run Alembic upgrade/downgrade with args

---

### Phase 4: FastAPI & API Layer (Days 6–7)

**Day 6 AM: FastAPI Skeleton**
1. Create `app/api/main.py`:
   - FastAPI app instance
   - Middleware setup (logging, CORS, exception handlers)
   - Exception handlers for custom errors
   - Startup/shutdown events (DB connection, logging setup)
   - API version prefix
   - Root endpoint `/` (welcome message)
   - Root endpoint `/health` (redirect to health router or inline)

2. Create `app/api/health.py`:
   - GET `/health` → returns {"status": "ok", "timestamp": "..."}
   - GET `/health/db` → checks DB connection, returns status
   - GET `/health/ready` → readiness check for K8s (deferred to later, stub for now)

3. Router registration:
   - Include health router
   - Include analytics router (in progress)

**Day 6 PM: Analytics Endpoints**
1. Create `app/api/routes/analytics.py`:
   - GET `/api/analytics/kpis`:
     - Query parameters: date_from, date_to (optional, defaults to YTD)
     - Response: KPISchema with revenue, orders, delay_rate, OTIF, lead_time
     - Implementation: calls AnalyticsService.compute_*_kpi() functions
   
   - GET `/api/analytics/suppliers`:
     - Query parameters: limit (default 10), offset (default 0), sort_by (default "risk_score")
     - Response: paginated SupplierMetricsSchema array
     - Implementation: calls AnalyticsService.get_top_suppliers_by_risk()

2. Create `app/api/routes/data.py` (placeholder for Sprint 1):
   - POST `/api/data/upload`:
     - Accept CSV file
     - Call ETL service
     - Return: {"status": "success", "rows_inserted": N, "errors": []}
   
   - GET `/api/data/status`:
     - Return upload status/stats (placeholder for Sprint 1)

3. All endpoints:
   - Type-hinted
   - Async where applicable
   - Proper HTTP status codes (200, 201, 400, 404, 500)
   - Logging of requests/responses
   - Dependency injection (get_db)

---

### Phase 5: Testing & Validation (Days 8–9)

**Day 8 AM: Test Configuration & Fixtures**
1. Create `tests/conftest.py`:
   - Pytest fixtures:
     - test_db: temporary test database (SQLite or PostgreSQL test instance)
     - client: TestClient for FastAPI
     - session: database session for tests
     - sample_suppliers, sample_orders, sample_shipments (factories)
   - Autouse fixture to reset DB before each test

2. Create `tests/fixtures/sample_data.py`:
   - Factory functions or FactoryBoy factories for models
   - Helper functions to create realistic test data

**Day 8 PM: Unit Tests**
1. Create `tests/unit/test_config.py`:
   - Test environment variable loading
   - Test config defaults
   - Test validation (missing required vars)

2. Create `tests/unit/test_models.py`:
   - Test model creation
   - Test constraints (FK relationships, NOT NULL, etc.)
   - Test timestamp fields (auto-update)

3. Create `tests/unit/test_schemas.py`:
   - Test Pydantic validation
   - Test field type coercion
   - Test custom validators

4. Create `tests/unit/test_etl.py`:
   - Test CSV parsing
   - Test validation logic
   - Test error handling (invalid data, duplicates)

5. Create `tests/unit/test_analytics.py`:
   - Test KPI computations with known data
   - Verify aggregation logic
   - Test edge cases (empty data, partial data)

6. Create `tests/unit/test_data_generator.py`:
   - Test synthetic data generation
   - Verify referential integrity
   - Check data distributions

**Day 9 AM: Integration Tests**
1. Create `tests/integration/test_api_health.py`:
   - GET `/health` → returns 200 {"status": "ok"}
   - GET `/health/db` → returns 200 {"status": "ok"} (DB connected)
   - Test with no database → returns 503 (service unavailable)

2. Create `tests/integration/test_api_analytics.py`:
   - Seed DB with known data
   - GET `/api/analytics/kpis` → verify correct calculations
   - GET `/api/analytics/suppliers` → verify pagination, sorting
   - Test error cases (invalid parameters)

3. Create `tests/integration/test_database.py`:
   - Test Alembic migrations (upgrade/downgrade)
   - Test schema creation
   - Test connection pooling

**Day 9 PM: Docker & Environment**
1. Create `Dockerfile.api`:
   - Base: python:3.11-slim
   - Install dependencies
   - Copy app code
   - Expose port 8000
   - Entrypoint: Uvicorn command

2. Create `docker/entrypoint.api.sh`:
   - Run migrations: `alembic upgrade head`
   - Seed database: `python scripts/seed_db.py` (if ENV=development)
   - Start Uvicorn: `uvicorn app.api.main:app --host 0.0.0.0 --port 8000`

3. Create `docker-compose.yml`:
   - PostgreSQL 15 service (image: postgres:15-alpine)
     - Environment: POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
     - Volume for persistence
   - API service (build: ./docker/Dockerfile.api)
     - Environment: DATABASE_URL, DEBUG, LOG_LEVEL
     - Ports: 8000:8000
     - Depends on: db
     - Volumes (dev): ./app:/app/app (hot-reload)
   - Streamlit service (placeholder, minimal config for Sprint 1)

4. Create `docker-compose.override.yml` (local dev):
   - Map ports for PostgreSQL (5432:5432) for direct access
   - Set DEBUG=true, LOG_LEVEL=DEBUG

---

### Phase 6: Documentation & Finalization (Days 10)

**Day 10 AM: Documentation**
1. Create `docs/SETUP.md`:
   - Prerequisites (Python 3.11+, Docker, Docker Compose)
   - Local dev setup: clone, create .env.local, `docker compose up`
   - Running tests: `pytest tests/`
   - Running migrations: `alembic upgrade head`
   - Seeding data: `python scripts/seed_db.py`

2. Create `docs/DATABASE.md`:
   - ER diagram (textual representation or reference to Mermaid)
   - Table descriptions
   - Relationships and constraints
   - Indexes and query patterns

3. Create `docs/API.md`:
   - OpenAPI/Swagger link: http://localhost:8000/docs
   - Endpoint summary table
   - Response examples
   - Error codes and meanings

4. Update `README.md`:
   - Project overview
   - Quick start (Docker Compose)
   - Links to docs (SETUP.md, DATABASE.md, API.md)
   - Roadmap (link to Implementation Blueprint)

5. Create `CONTRIBUTING.md`:
   - Code style (Black, Ruff)
   - Type hints required
   - Test coverage expectations (≥80%)
   - PR process, commit message format

**Day 10 PM: Quality Assurance & Handoff**
1. Run full test suite:
   - `pytest tests/ -v --cov=app --cov-report=html`
   - Target: ≥80% code coverage
   - Fix any failures

2. Linting & formatting:
   - Black: `black app/ tests/`
   - Ruff: `ruff check app/ tests/`
   - Type checking: `mypy app/` (optional, warn-level)

3. Docker testing:
   - `docker compose build`
   - `docker compose up` (all services running without errors)
   - Verify endpoints: curl http://localhost:8000/health
   - Verify DB connection: curl http://localhost:8000/health/db

4. Create `SPRINT_1_COMPLETION.md`:
   - List of deliverables (checked off)
   - Test results (coverage, passing tests)
   - Known issues or tech debt (noted for Sprint 2)
   - Sign-off checklist

---

## PART III: EXACT FILES TO CREATE (Checklist)

### Directory Structure (10 directories)
- [ ] `.github/workflows/`
- [ ] `.vscode/`
- [ ] `alembic/versions/`
- [ ] `app/core/`, `app/models/`, `app/schemas/`, `app/api/routes/`, `app/services/`, `app/db/`, `app/utils/`
- [ ] `tests/unit/`, `tests/integration/`, `tests/fixtures/`
- [ ] `scripts/`
- [ ] `docker/`
- [ ] `logs/`, `data/raw/`, `data/processed/`
- [ ] `docs/`

### Python Source Files (45 files)
**app/core/ (4 files)**
- [ ] `app/core/__init__.py`
- [ ] `app/core/config.py` (Pydantic BaseSettings, ~120 lines)
- [ ] `app/core/database.py` (SQLAlchemy setup, ~80 lines)
- [ ] `app/core/logging.py` (structured logging, ~100 lines)
- [ ] `app/core/constants.py` (constants, ~50 lines)

**app/models/ (10 files)**
- [ ] `app/models/__init__.py`
- [ ] `app/models/base.py` (base classes, ~40 lines)
- [ ] `app/models/supplier.py` (Supplier, SupplierRiskScore, ~60 lines)
- [ ] `app/models/order.py` (Order, ~50 lines)
- [ ] `app/models/shipment.py` (Shipment, ShipmentTracking, ~70 lines)
- [ ] `app/models/product.py` (Product, ~50 lines)
- [ ] `app/models/inventory.py` (Inventory, InventorySnapshot, ~60 lines)
- [ ] `app/models/warehouse.py` (Warehouse, ~40 lines)
- [ ] `app/models/risk_score.py` (RiskScore, SCRIScore, ~60 lines)
- [ ] `app/models/simulation.py` (SimulationRun, SimulationResult, ~80 lines)

**app/schemas/ (8 files)**
- [ ] `app/schemas/__init__.py`
- [ ] `app/schemas/base.py` (base schemas, ~50 lines)
- [ ] `app/schemas/supplier.py` (SupplierSchema variants, ~80 lines)
- [ ] `app/schemas/shipment.py` (ShipmentSchema variants, ~80 lines)
- [ ] `app/schemas/analytics.py` (KPISchema, AnalyticsSchema, ~100 lines)
- [ ] `app/schemas/prediction.py` (placeholder, ~30 lines)
- [ ] `app/schemas/risk.py` (placeholder, ~30 lines)
- [ ] `app/schemas/resilience.py` (placeholder, ~30 lines)
- [ ] `app/schemas/simulation.py` (placeholder, ~30 lines)

**app/api/ (3 files)**
- [ ] `app/api/__init__.py`
- [ ] `app/api/main.py` (FastAPI app, ~150 lines)
- [ ] `app/api/health.py` (health router, ~50 lines)

**app/api/routes/ (2 files)**
- [ ] `app/api/routes/__init__.py`
- [ ] `app/api/routes/analytics.py` (analytics endpoints, ~100 lines)
- [ ] `app/api/routes/data.py` (data endpoints placeholder, ~80 lines)

**app/services/ (3 files)**
- [ ] `app/services/__init__.py`
- [ ] `app/services/etl.py` (ETL pipeline, ~200 lines)
- [ ] `app/services/analytics.py` (KPI computation, ~150 lines)
- [ ] `app/services/data_generator.py` (synthetic data, ~300 lines)

**app/db/ (2 files)**
- [ ] `app/db/__init__.py`
- [ ] `app/db/session.py` (DB session dependency, ~50 lines)
- [ ] `app/db/crud.py` (CRUD helpers, ~150 lines)

**app/utils/ (4 files)**
- [ ] `app/utils/__init__.py`
- [ ] `app/utils/errors.py` (custom exceptions, ~80 lines)
- [ ] `app/utils/validators.py` (Pydantic validators, ~100 lines)
- [ ] `app/utils/helpers.py` (utility functions, ~100 lines)

**app/ (1 file)**
- [ ] `app/__init__.py`

**tests/ (10+ files)**
- [ ] `tests/__init__.py`
- [ ] `tests/conftest.py` (pytest fixtures, ~150 lines)
- [ ] `tests/unit/__init__.py`
- [ ] `tests/unit/test_config.py` (~80 lines)
- [ ] `tests/unit/test_models.py` (~120 lines)
- [ ] `tests/unit/test_schemas.py` (~100 lines)
- [ ] `tests/unit/test_etl.py` (~150 lines)
- [ ] `tests/unit/test_analytics.py` (~120 lines)
- [ ] `tests/unit/test_data_generator.py` (~100 lines)
- [ ] `tests/integration/__init__.py`
- [ ] `tests/integration/test_api_health.py` (~80 lines)
- [ ] `tests/integration/test_api_analytics.py` (~120 lines)
- [ ] `tests/integration/test_database.py` (~100 lines)
- [ ] `tests/fixtures/__init__.py`
- [ ] `tests/fixtures/sample_data.py` (~200 lines)

**scripts/ (4 files)**
- [ ] `scripts/__init__.py`
- [ ] `scripts/seed_db.py` (~150 lines)
- [ ] `scripts/reset_db.py` (~100 lines)
- [ ] `scripts/migrate_db.py` (~80 lines)

**Alembic Migration Files (2 files)**
- [ ] `alembic/__init__.py`
- [ ] `alembic/env.py` (modified Alembic environment)
- [ ] `alembic/script.py.mako` (migration template)
- [ ] `alembic/alembic.ini` (config)
- [ ] `alembic/versions/__init__.py`
- [ ] `alembic/versions/001_initial_schema.py` (~400 lines: all DDL)

### Docker Files (3 files)
- [ ] `Dockerfile.api`
- [ ] `Dockerfile.streamlit` (minimal for Sprint 1)
- [ ] `docker/entrypoint.api.sh`
- [ ] `docker/entrypoint.streamlit.sh`

### Configuration Files (10+ files)
- [ ] `.gitignore`
- [ ] `.dockerignore`
- [ ] `.python-version`
- [ ] `.env.example`
- [ ] `.env.test`
- [ ] `.env.docker`
- [ ] `.vscode/launch.json` (debug config)
- [ ] `.vscode/settings.json` (Python formatting)
- [ ] `.github/workflows/ci.yml` (placeholder)
- [ ] `pyproject.toml` (project metadata, dependencies, tools)
- [ ] `requirements.txt` (pinned dependencies)
- [ ] `requirements-dev.txt` (dev dependencies)
- [ ] `Makefile` (convenience commands)
- [ ] `docker-compose.yml`
- [ ] `docker-compose.override.yml`

### Documentation Files (6+ files)
- [ ] `docs/SETUP.md`
- [ ] `docs/DATABASE.md`
- [ ] `docs/API.md`
- [ ] `docs/SPRINT_1_COMPLETION.md`
- [ ] `README.md` (updated)
- [ ] `CONTRIBUTING.md`

### Total: ~80+ files

---

## PART IV: ACCEPTANCE CRITERIA (Testing & Validation)

### Functional Acceptance Criteria

**1. Repository & Project Setup**
- [ ] Git repo initialized with clean commit history
- [ ] `.python-version` set to 3.11.x
- [ ] `requirements.txt` and `requirements-dev.txt` pinned and compatible
- [ ] `pyproject.toml` complete with project metadata and tool configs
- [ ] `.gitignore` and `.dockerignore` in place (no __pycache__, .env, etc.)
- [ ] All import paths work (no circular imports)
- [ ] IDE (VS Code) config present with Python environment setup

**2. Environment & Configuration**
- [ ] `app/core/config.py` loads all required ENV vars from `.env` files
- [ ] Config validation fails gracefully with clear error messages if required vars missing
- [ ] Config supports DEBUG, LOG_LEVEL, DATABASE_URL, API_PORT, etc.
- [ ] `.env.example` template accurate and complete
- [ ] Environment-specific configs (`.env.test`, `.env.docker`) functional

**3. Database Layer**
- [ ] PostgreSQL connection string works (verify with `psql`)
- [ ] SQLAlchemy engine initializes without errors
- [ ] Connection pooling configured (defaults: min_size=5, max_size=20)
- [ ] All 10 SQLAlchemy models defined with:
  - Type hints on all fields
  - Foreign key relationships
  - Proper nullable/NOT NULL constraints
  - Indexes on frequently-queried columns
  - Timestamp fields (created_at, updated_at) with auto-update

**4. Database Schema & Migrations**
- [ ] Alembic initialized and configured
- [ ] First migration (`001_initial_schema.py`) creates all 10 tables
- [ ] Migration up: `alembic upgrade head` creates schema without errors
- [ ] Migration down: `alembic downgrade -1` successfully rolls back
- [ ] Schema matches entity-relationship diagram (all FKs, indexes present)
- [ ] Schema verified in PostgreSQL (inspect with psql or GUI tool)
- [ ] No schema conflicts or circular dependencies

**5. Pydantic Schemas**
- [ ] All 8 schema modules present and complete
- [ ] Base schemas (TimestampSchema, BaseSchema) functional and reused
- [ ] Type hints on all fields (str, int, float, datetime, Optional, List, etc.)
- [ ] Validators working (custom validators pass/fail as expected)
- [ ] Serialization/deserialization works (Pydantic → JSON → Pydantic)
- [ ] Schema validation catches bad data (raises ValidationError)

**6. Data Layer (CRUD & Database Utilities)**
- [ ] `app/db/crud.py` CRUD functions work (create, read, update, delete)
- [ ] Query helpers functional (get_suppliers, get_shipments_in_window, etc.)
- [ ] Pagination working (limit, offset parameters)
- [ ] Transactions managed correctly (rollback on error)
- [ ] Connection pooling / session lifecycle working

**7. Synthetic Data Generation**
- [ ] `data_generator.py` generates:
  - 100 suppliers with realistic data
  - 50 products with categories and pricing
  - 1,000 orders with random assignments
  - 5,000 shipments with lead times and delays
  - 250 inventory snapshots
  - 5 warehouses
- [ ] Data referential integrity maintained (all FKs valid)
- [ ] Data distributions realistic:
  - Lead times: LogNormal-like distributions
  - Delays: Bernoulli-distributed
  - Supplier on-time rates: range [0.7, 0.95]
  - Orders: diverse across regions and products
- [ ] Deterministic output when seeded (reproducible)
- [ ] Generated data can be inserted into database without errors

**8. ETL Pipeline**
- [ ] CSV ingestion works (reads, parses, validates structure)
- [ ] Data validation catches issues:
  - Type mismatches (e.g., string in numeric field)
  - Missing required fields
  - Constraint violations (e.g., negative amounts)
  - Duplicates
- [ ] Cleansing logic handles:
  - NULL values (log and decide: drop vs default)
  - Outliers (flag, log, optionally filter)
  - Formatting issues
- [ ] Error logging detailed (row number, error message, suggested fix)
- [ ] Transaction management correct (batch inserts rolled back on critical error)
- [ ] ETL returns meaningful status (rows processed, inserted, errors)

**9. Analytics Service**
- [ ] KPI computation functions all work:
  - compute_revenue_kpi() returns YTD revenue, MoM %, targets
  - compute_order_kpi() returns order stats
  - compute_delay_kpi() returns delay metrics by supplier/region
  - compute_otif_kpi() returns on-time in-full %
  - compute_lead_time_kpi() returns lead-time stats
- [ ] Supplier metrics functions work (top suppliers, performance details)
- [ ] Aggregations mathematically correct (verified with sample data)
- [ ] Edge cases handled (empty data, partial windows, no history)
- [ ] Query performance acceptable (<1s for typical KPI queries on sample data)

**10. FastAPI Application**
- [ ] FastAPI app initializes without errors
- [ ] Middleware loaded (logging, exception handlers, CORS if needed)
- [ ] Exception handlers catch and format errors properly
- [ ] Startup events run (DB connection, logging setup)
- [ ] Shutdown events run (cleanup)
- [ ] Root endpoint `/` returns welcome message
- [ ] OpenAPI/Swagger docs available at `/docs`
- [ ] ReDoc available at `/redoc`

**11. Health Endpoints**
- [ ] GET `/health` returns 200 with {"status": "ok", "timestamp": "ISO-8601"}
- [ ] GET `/health/db` returns 200 if DB connected, 503 if not
- [ ] Health endpoints async and fast (<100ms)
- [ ] Proper HTTP status codes (200 for OK, 503 for unavailable)

**12. Analytics Endpoints**
- [ ] GET `/api/analytics/kpis`:
  - Returns KPI data for date range (defaults to YTD)
  - Response schema matches KPISchema
  - Values are reasonable (revenue > 0, rates in [0,1], etc.)
  - Query parameters (date_from, date_to) respected
  - HTTP 200 on success, 400 on bad parameters

- [ ] GET `/api/analytics/suppliers`:
  - Returns paginated supplier list
  - Sorting works (sort_by parameter)
  - Pagination works (limit, offset)
  - Response schema matches SupplierMetricsSchema[]
  - HTTP 200 on success

- [ ] All endpoints:
  - Type-hinted parameters and return types
  - Async where applicable
  - Proper error responses (400, 404, 500)
  - Request/response logged
  - <500ms latency for typical queries

**13. Data Upload Endpoints (Placeholder)**
- [ ] POST `/api/data/upload` accepts CSV file
- [ ] Returns {"status": "success", "rows_inserted": N} or error
- [ ] GET `/api/data/status` returns upload statistics

**14. Testing**
- [ ] Unit tests:
  - `test_config.py`: ≥5 tests (env vars, defaults, validation)
  - `test_models.py`: ≥10 tests (model creation, constraints, timestamps)
  - `test_schemas.py`: ≥10 tests (validation, serialization)
  - `test_etl.py`: ≥15 tests (CSV parsing, validation, error handling)
  - `test_analytics.py`: ≥10 tests (KPI calculations, edge cases)
  - `test_data_generator.py`: ≥10 tests (data integrity, distributions)
  - Total: ≥60 unit tests

- [ ] Integration tests:
  - `test_api_health.py`: ≥5 tests (health endpoints)
  - `test_api_analytics.py`: ≥10 tests (analytics endpoints, edge cases)
  - `test_database.py`: ≥5 tests (migrations, schema, connection)
  - Total: ≥20 integration tests

- [ ] Test suite execution:
  - `pytest tests/ -v` passes ≥80 tests
  - Code coverage ≥80% (app/ code)
  - No warnings or deprecation errors

- [ ] Test fixtures:
  - Conftest provides fixtures for db, client, sample data
  - Tests use fixtures (no hardcoded test data in individual test functions)
  - Autouse fixture cleans up between tests

**15. Docker & Containerization**
- [ ] `Dockerfile.api` builds without errors
- [ ] `Dockerfile.streamlit` builds without errors
- [ ] `docker-compose.yml` defines all services:
  - PostgreSQL (15-alpine)
  - API (FastAPI)
  - Streamlit (placeholder)
- [ ] Entrypoints work:
  - `docker/entrypoint.api.sh` runs migrations and starts Uvicorn
  - `docker/entrypoint.streamlit.sh` starts Streamlit
- [ ] Docker Compose stack:
  - `docker compose build` completes without errors
  - `docker compose up` brings up all services
  - Services ready and responsive within 30s
  - Container logs clean (no errors, only startup messages)
- [ ] Environment variables:
  - `.env.docker` loaded correctly in containers
  - Database URL properly set for API to connect to PostgreSQL
  - No hardcoded secrets in images or compose files

**16. Code Quality**
- [ ] Black formatting passes: `black app/ tests/` (idempotent)
- [ ] Ruff linting passes: `ruff check app/ tests/` (no errors, minimal warnings)
- [ ] Type hints present on:
  - All function parameters (with defaults specified)
  - All function return types
  - All class attributes
- [ ] Docstrings present on:
  - All public classes
  - All public functions
  - All complex private functions
  - Format: Google-style or NumPy-style, consistent
- [ ] Logging:
  - All service functions log entry/exit or key operations
  - All errors logged with context
  - No print() statements (use logging)
  - Log levels used appropriately (DEBUG, INFO, WARNING, ERROR)
- [ ] Error handling:
  - Custom exceptions used (not generic Exception)
  - Database errors caught and logged
  - API errors return proper HTTP status codes

**17. Documentation**
- [ ] `README.md`:
  - Project overview (1 paragraph)
  - Quick start with Docker (3–5 steps)
  - Links to SETUP.md, DATABASE.md, API.md
  - Project roadmap link
  - Contributing guidelines link
- [ ] `SETUP.md`:
  - Prerequisites listed
  - Local dev setup (clone, env, docker compose)
  - How to run tests
  - How to run migrations
  - How to seed data
  - Troubleshooting section
- [ ] `DATABASE.md`:
  - ER diagram (ASCII or Mermaid reference)
  - Table descriptions (10 tables)
  - Relationships and FKs
  - Key indexes
- [ ] `API.md`:
  - Swagger URL: http://localhost:8000/docs
  - Endpoint summary (all 5–6 endpoints)
  - Example requests/responses
  - Error codes (400, 404, 500, etc.)
- [ ] `CONTRIBUTING.md`:
  - Code style (Black, Ruff)
  - Type hints required
  - Test coverage expectations
  - PR process
- [ ] All docstrings in code (not just external docs)

**18. Deployment Readiness**
- [ ] Health check endpoints functional
- [ ] Environment variables externalized (no secrets in code)
- [ ] Database migrations versioned and runnable
- [ ] Logging configured for production (JSON structured logs, file + stdout)
- [ ] Error handling and graceful degradation
- [ ] Docker images build and run cleanly
- [ ] No development dependencies in production Dockerfile (pyproject.toml [dev] vs [prod])

---

## PART V: DEFINITION OF DONE (End of Sprint 1)

A deliverable is considered **DONE** when:

1. ✅ **Code written, reviewed, and merged to main branch**
2. ✅ **Tests written and passing** (unit + integration)
3. ✅ **Code formatted** (Black) and linted (Ruff) with no errors
4. ✅ **Type hints complete** (100% of function signatures)
5. ✅ **Docstrings present** (all public APIs documented)
6. ✅ **Logging implemented** (all key operations logged)
7. ✅ **Error handling in place** (custom exceptions, proper HTTP codes)
8. ✅ **Documentation updated** (README, API docs, SETUP guide)
9. ✅ **Docker & Compose tested** (`docker compose up` works)
10. ✅ **No hardcoded secrets** (all ENV variables)
11. ✅ **Deployment ready** (can be deployed to staging/production without code changes)

---

## PART VI: RISKS & MITIGATION

| Risk | Mitigation |
|------|-----------|
| Schema design flaws discovered mid-sprint | Create comprehensive ER diagram review (day 2); peer review migrations |
| Synthetic data unrealistic | Validate distributions with domain knowledge; document assumptions |
| Performance issues on large datasets | Add indexes early; profile queries; cache aggregations |
| Test brittleness (flaky tests) | Use fixtures properly; avoid hardcoded dates; use factories |
| Docker environment drift | Use docker-compose.override.yml for consistent local dev; pin base image versions |
| Scope creep (feature requests during Sprint 1) | Track in GitHub issues; defer to Sprint 2 planning |
| Dependency conflicts | Pin all versions; use requirements-lock files for reproducibility |

---

## PART VII: HAND-OFF TO SPRINT 2

At end of Sprint 1, deliver:

1. **Code Repository**
   - Clean main branch with Sprint 1 tag
   - All tests passing
   - Full documentation
   - Docker stack runnable

2. **Artifacts**
   - ERD (entity-relationship diagram)
   - API endpoint summary
   - Test coverage report
   - Performance baseline (KPI query times)

3. **Technical Debt Log**
   - Known issues (with priority: P0/P1/P2)
   - Future improvements (marked with TODO comments in code)
   - Architecture decisions recorded (in ADRs or docs/)

4. **Sprint 2 Dependencies**
   - Foundation is solid and tested
   - Ready for: ML models, SCRI computation, Digital Twin, more endpoints
   - No blockers; all basic infrastructure in place

---

## SUMMARY TABLE

| Deliverable | Owner | Owner Effort | Key Dependencies | Success Metric |
|---|---|---|---|---|
| Project Setup & Deps | Engineer | 1 day | None | Requirements install, no conflicts |
| Config & Environment | Engineer | 0.5 day | Dependencies | Config loads from ENV, all vars present |
| Logging & Error Handling | Engineer | 0.5 day | Config | Structured logs, custom exceptions |
| Database & Models | Engineer | 1.5 days | Config | Schema created, models defined with FKs |
| Alembic Migrations | Engineer | 0.5 day | Models | Migrations upgrade/downgrade successfully |
| CRUD & Session Mgmt | Engineer | 0.5 day | Database | CRUD functions work, transactions safe |
| Synthetic Data Generator | Engineer | 1 day | Models | 5k+ records generated, referential integrity |
| ETL Pipeline | Engineer | 1.5 days | Generator, Models | CSV import, validation, error handling |
| Analytics Service | Engineer | 1 day | Models, CRUD | KPIs computed correctly, <1s queries |
| FastAPI App & Middleware | Engineer | 1 day | Config, Logging | App starts, docs available, errors handled |
| Health & Analytics Endpoints | Engineer | 1 day | FastAPI, Analytics Service | Endpoints respond, schema matches, <500ms |
| Docker & Compose | Engineer | 1 day | All | Stack brings up services in <30s |
| Unit Tests | Engineer | 2 days | All modules | ≥60 tests, ≥80% coverage |
| Integration Tests | Engineer | 1 day | Docker, Endpoints | ≥20 tests, all APIs tested |
| Documentation | Engineer | 1 day | All | README, SETUP, API, DATABASE, CODE DOCS |
| **Total** | **1 Engineer** | **~14 days** | **None** | **All criteria met** |

---

## NEXT: SPRINT 2

Sprint 2 will build on Sprint 1 foundation to add:
- Delay Prediction models (trainer, inference)
- Supplier Risk Scoring logic
- SCRI computation (drivers, aggregation)
- Digital Twin engine (deterministic)
- Prediction, Risk, Resilience, Simulation endpoints
- Streamlit dashboard pages (executive, SCRI, supplier, delay, twin)

