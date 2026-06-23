# SupplyChainIQ Folder Structure

This repository is organized for production-grade data science and analytics.

- `app/`
  - `api/`
    - `main.py` - FastAPI application entrypoint
    - `routes/` - API route modules
    - `schemas/` - Pydantic request and response models
  - `core/`
    - `config.py` - environment and configuration handling
    - `database.py` - PostgreSQL connection factory
    - `logging.py` - structured logging configuration
  - `services/`
    - `etl.py` - ingestion, validation, staging, and persistence
    - `profiling.py` - data profiling and quality reports
    - `analytics.py` - KPI calculation and aggregation logic
    - `prediction.py` - model inference and scoring APIs
    - `risk.py` - supplier risk score calculation
    - `resilience.py` - SCRI engine and score breakdown
    - `simulation.py` - digital twin scenario engine
    - `copilot.py` - structured reasoning and executive assistant logic
  - `models/`
    - `trainer.py` - training pipeline and evaluation orchestration
    - `model_registry.py` - local model metadata and versioning
    - `explainability.py` - SHAP interpretability utilities
  - `db/`
    - `schemas.sql` - PostgreSQL schema definitions
  - `streamlit_app/`
    - `app.py` - Streamlit multi-page app launcher
    - `pages/` - dashboard pages for each product module
- `data/`
  - `raw/` - uploaded CSV files and raw data snapshots
  - `processed/` - cleaned feature datasets and training tables
  - `profiles/` - data quality reports and profiling outputs
- `docs/` - architecture, API design, ML design, dashboard UX, sprint plan
- `tests/` - unit and integration tests
- `Dockerfile`, `docker-compose.yml` - container deployment
- `.env.example` - environment variable template
- `requirements.txt` - Python dependency manifest
