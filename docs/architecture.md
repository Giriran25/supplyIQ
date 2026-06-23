# System Architecture

## Components

- `FastAPI Backend` - provides data ingestion, analytics, machine learning inference, supplier risk scoring, SCRI calculation, simulation, and AI Copilot APIs.
- `PostgreSQL Database` - stores suppliers, products, orders, shipments, inventory, risk scores, and simulation results.
- `Streamlit Dashboard` - frontend interface for executive dashboards, analytics, prediction, resilience monitoring, simulation, and AI Copilot.
- `Machine Learning` - training pipeline for delay prediction and explainability using Logistic Regression, XGBoost, and SHAP.
- `AI Copilot` - structured query assistant using LangChain and OpenAI.

## Data Flow

1. Raw CSV data is uploaded through the `data/upload` endpoint.
2. The ETL service validates and profiles data, then loads it into PostgreSQL.
3. Analytics services query PostgreSQL for KPIs, supplier performance, and logistics metrics.
4. The ML service reads training data, engineers features, trains models, and writes predictions to the API.
5. The resilience engine computes an SCRI score from supplier diversity, geographic diversity, lead time stability, supplier reliability, and inventory buffer strength.
6. The simulation engine runs digital twin scenarios and returns revenue, inventory, delay, and service impacts.
7. The AI Copilot uses structured data retrieval to answer executive questions and provide recommended actions.

## Service Boundaries

- Data Platform: ingestion, validation, profiling, and persistence
- Analytics: KPI aggregation, supplier/product/regional analysis
- Prediction: delay probability and class inference
- Risk Intelligence: supplier reliability and risk scoring
- Resilience: SCRI computation and validation
- Simulation: digital twin scenario execution
- Copilot: natural-language executive assistance

## Deployment

- Containerized with Docker and Docker Compose
- `db` service for PostgreSQL
- `api` service for FastAPI
- `dashboard` service for Streamlit
- Environment variables managed through `.env`
