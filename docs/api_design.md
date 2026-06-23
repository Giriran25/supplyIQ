# API Design

## Service Boundary

The FastAPI backend provides ingest, analytics, prediction, risk, resilience, simulation, and copilot endpoints.

### Endpoints

#### `POST /api/data/upload`
- Request: `DataUploadRequest`
- Response: `DataUploadResponse`
- Purpose: upload CSV, validate schema, stage raw data.

#### `GET /api/data/profile`
- Query params: `dataset_name`
- Response: `DataProfileResponse`
- Purpose: return profiling summary and quality checks.

#### `POST /api/analytics/kpis`
- Request: `AnalyticsRequest`
- Response: `AnalyticsResponse`
- Purpose: compute revenue, orders, delay rate, on-time delivery, lead time.

#### `GET /api/analytics/suppliers`
- Response: `SupplierAnalyticsResponse`
- Purpose: supplier performance, delivery variance, top risks.

#### `POST /api/prediction/delay`
- Request: `DelayPredictionRequest`
- Response: `DelayPredictionResponse`
- Purpose: return delay probability, predicted class, confidence.

#### `GET /api/risk/supplier/{supplier_id}`
- Response: `SupplierRiskResponse`
- Purpose: supplier reliability, risk score, risk factors.

#### `GET /api/resilience/scri`
- Response: `SCRIResponse`
- Purpose: compute the Supply Chain Resilience Index and category.

#### `POST /api/simulation/run`
- Request: `SimulationRequest`
- Response: `SimulationResponse`
- Purpose: run digital twin scenarios and report impacts.

#### `POST /api/copilot/query`
- Request: `CopilotRequest`
- Response: `CopilotResponse`
- Purpose: structured AI assistant answering executive questions.

## Request / Response Schemas

### `DataUploadRequest`
- `dataset_name: str`
- `csv_payload: str`
- `source: str`

### `DataUploadResponse`
- `success: bool`
- `records_loaded: int`
- `errors: list[str]`

### `DelayPredictionRequest`
- `supplier_id: int`
- `product_id: int`
- `region: str`
- `lead_time_days: int`
- `order_value: float`
- `previous_delay_rate: float`
- `carrier_reliability: float`

### `DelayPredictionResponse`
- `delay_probability: float`
- `predicted_label: str`
- `model_name: str`
- `explanation: dict[str, float]`

### `SupplierRiskResponse`
- `supplier_id: int`
- `supplier_name: str`
- `reliability_score: float`
- `risk_score: float`
- `risk_factors: dict[str, float]`
- `recommendations: list[str]`

### `SCRIResponse`
- `scri_score: float`
- `category: str`
- `drivers: dict[str, float]`
- `validation_notes: str`

### `SimulationRequest`
- `scenario_type: str`
- `supplier_id: int | None`
- `product_id: int | None`
- `region: str | None`
- `impact_horizon_days: int`

### `SimulationResponse`
- `scenario_name: str`
- `revenue_impact: float`
- `inventory_impact: float`
- `delay_impact: float`
- `service_impact: float`
- `summary: str`

### `CopilotRequest`
- `query: str`
- `context_filter: dict[str, str] | None`

### `CopilotResponse`
- `answer: str`
- `supporting_metrics: dict[str, float]`
- `next_steps: list[str]`

## API Principles

- Use Pydantic for validation and type-safe request/response models.
- Keep endpoints stateless with explicit inputs.
- Support structured reasoning for the AI copilot.
- Log payloads and response status for analytics tracing.
