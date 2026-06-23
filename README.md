# SupplyChainIQ

**Tagline:** Predict. Simulate. Prevent.

SupplyChainIQ is a production-grade portfolio project for supply chain risk intelligence. It combines a Streamlit analytics dashboard with a FastAPI backend, PostgreSQL data platform, machine learning, explainable AI, digital twin simulation, and an AI executive copilot.

## Highlights

- Data ingestion and validation pipeline
- PostgreSQL-backed analytics and reporting
- Shipment delay prediction with Logistic Regression and XGBoost
- Supplier risk scoring and explainable AI using SHAP
- Supply Chain Resilience Index (SCRI)
- Digital twin simulation engine for disruption scenarios
- AI Copilot powered by structured reasoning, LangChain, and OpenAI
- Docker deployment and environment-driven configuration

## Repository Structure

See `docs/folder_structure.md` for the complete repository layout.

## Getting Started

1. Copy `.env.example` to `.env`
2. Build services with Docker Compose:
   ```bash
   docker compose up --build
   ```
3. Open Streamlit dashboard: `http://localhost:8501`
4. Open FastAPI docs: `http://localhost:8000/docs`

## Project Modules

- `app/api`: API endpoints and request/response schemas
- `app/services`: business logic for ETL, analytics, prediction, risk, resilience, simulation, and copilot
- `app/models`: training, explainability, and model registry
- `app/streamlit_app`: dashboard pages and UI flow
- `docs`: architectural design, sprint planning, and technical guidance
- `tests`: unit tests and integration checks

## Notes

This scaffold is intentionally modular and extensible, with production-grade conventions for clean code, logging, and type safety.
