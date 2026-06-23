# Sprint Plan

## Sprint 1: Data Platform

### Tasks
- Create PostgreSQL schema and database bootstrapping scripts
- Build upload and validation API
- Implement ETL pipeline and data profiling service
- Persist supplier, shipment, product, order, inventory, risk, and simulation records

### Files
- `app/api/routes/data_platform.py`
- `app/api/schemas/data.py`
- `app/services/etl.py`
- `app/services/profiling.py`
- `app/db/schemas.sql`
- `app/core/database.py`

### Deliverables
- Working CSV upload endpoint
- Data validation and quality report generation
- Data loaded into PostgreSQL

### Acceptance Criteria
- Uploaded datasets are validated and stored
- Data quality report includes completeness, uniqueness, missing values, and schema drift checks
- API returns clear success/failure messages

## Sprint 2: Analytics Dashboard

### Tasks
- Build KPI aggregation service
- Create analytics endpoints for supplier, product, logistics, and regional views
- Develop Streamlit dashboard pages for executive and analytics views
- Add Plotly visualizations and summary cards

### Files
- `app/services/analytics.py`
- `app/api/routes/analytics.py`
- `app/api/schemas/analytics.py`
- `app/streamlit_app/app.py`
- `app/streamlit_app/pages/1_executive_dashboard.py`
- `app/streamlit_app/pages/2_supplier_intelligence.py`

### Deliverables
- Analytics endpoints returning KPI and drill-down data
- Streamlit executive dashboard with KPI cards and trend charts
- Supplier analytics view with filters and ranking

### Acceptance Criteria
- Dashboard shows revenue, orders, delay rate, on-time delivery, and lead time
- Supplier and regional analytics update when filters change
- Plotly charts render with real sample data

## Sprint 3: ML Prediction

### Tasks
- Develop feature engineering helpers and training pipeline
- Train Logistic Regression and XGBoost delay prediction models
- Create prediction endpoint with probability and label output
- Add SHAP explainability for model predictions

### Files
- `app/models/trainer.py`
- `app/services/prediction.py`
- `app/api/routes/predictions.py`
- `app/api/schemas/prediction.py`
- `app/models/explainability.py`
- `app/models/model_registry.py`

### Deliverables
- Prediction API returning delay probability and class
- SHAP explainability available for each inference
- Model registry tracking model versions and metrics

### Acceptance Criteria
- Model returns predictions from sample data
- Metrics are logged and accessible in registry
- SHAP values provide interpretable feature impact

## Sprint 4: Supplier Intelligence

### Tasks
- Build supplier risk scoring engine
- Implement supplier reliability and risk factor calculations
- Add supplier risk endpoint and dashboard detail page
- Expose recommendations and risk drivers

### Files
- `app/services/risk.py`
- `app/api/routes/risk.py`
- `app/api/schemas/risk.py`
- `app/streamlit_app/pages/2_supplier_intelligence.py`

### Deliverables
- Supplier risk API and dashboard view
- Reliability score and risk score formulas
- Risk factor breakdown for each supplier

### Acceptance Criteria
- Supplier risk endpoint returns 0-100 score
- Dashboard shows high-risk suppliers and activity drivers
- Recommendations are produced from risk analysis

## Sprint 5: SCRI

### Tasks
- Design SCRI scoring framework and validation methodology
- Build SCRI service with diversity and stability drivers
- Create SCRI endpoint and dashboard page
- Document formula and feature engineering

### Files
- `app/services/resilience.py`
- `app/api/routes/resilience.py`
- `app/api/schemas/resilience.py`
- `app/streamlit_app/pages/4_scri_dashboard.py`
- `docs/ml_architecture.md`

### Deliverables
- SCRI score computation and category output
- Dashboard explaining score drivers and recommendations
- Validation notes for resilience scoring

### Acceptance Criteria
- SCRI returns a 0-100 score and category
- Score drivers are visible and interpretable
- Business validation methodology is documented

## Sprint 6: Digital Twin

### Tasks
- Create digital twin engine for scenario simulation
- Define entities for suppliers, warehouses, products, and regions
- Implement scenario endpoints and dashboard interaction
- Report revenue, inventory, delay, and service impacts

### Files
- `app/services/simulation.py`
- `app/api/routes/simulation.py`
- `app/api/schemas/simulation.py`
- `app/streamlit_app/pages/5_digital_twin_simulation.py`

### Deliverables
- Simulation engine with four scenario types
- Scenario output and impact tables
- Dashboard simulation controls and results view

### Acceptance Criteria
- Simulation endpoint returns a detailed impact summary
- Dashboard allows scenario selection and displays results
- Scenarios are reproducible with structured inputs

## Sprint 7: AI Copilot

### Tasks
- Build structured copilot service for executive questions
- Integrate LangChain with OpenAI for prompt-based reasoning
- Add endpoint and Streamlit AI assistant page
- Support analytics, risk, SCRI, and simulation queries

### Files
- `app/services/copilot.py`
- `app/api/routes/copilot.py`
- `app/api/schemas/copilot.py`
- `app/streamlit_app/pages/6_ai_copilot.py`

### Deliverables
- AI Copilot endpoint answering executive questions
- Natural-language interface in dashboard
- Structured metric retrieval for responses

### Acceptance Criteria
- Copilot returns accurate summaries for sample queries
- Responses include supporting metrics and next steps
- System uses structured reasoning without RAG complexity

## Sprint 8: Deployment

### Tasks
- Finalize Dockerfile and Docker Compose
- Add environment variable configuration and secrets handling
- Create CI-friendly test scripts
- Document deployment and onboarding

### Files
- `Dockerfile`
- `docker-compose.yml`
- `README.md`
- `tests/test_api.py`
- `tests/test_services.py`

### Deliverables
- Running containerized app stack
- Deployment documentation
- Basic unit tests and smoke checks

### Acceptance Criteria
- `docker compose up --build` launches API and dashboard
- API docs available at `/docs`
- Dashboard available at `http://localhost:8501`
- Unit tests pass for core services
