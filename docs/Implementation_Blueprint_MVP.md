# SupplyChainIQ: Technical Implementation Blueprint
## From SCRI v2 Research Design to MVP Deployment (6–8 Weeks)

---

## PART I: MVP SCOPE DEFINITION

### 1.1 Core MVP (Weeks 1–6): Minimum Deployable Project

**What IS in MVP:**
- Delay Prediction: baseline logistic regression + XGBoost, simple SHAP explainability
- Supplier Risk: three-factor scoring (delay frequency, delivery variance, concentration) with static weights
- SCRI: simplified hybrid (multiplicative core for diversity+buffer, additive for reliability+stability, NO graph modifier initially, NO full Bayesian)
- Digital Twin: deterministic baseline engine (single-run scenarios, no Monte Carlo initially)
- Analytics: core KPI dashboard (revenue, orders, delay rate, OTIF, lead time)
- Streamlit UI: 4–5 core pages (executive, supplier risk, delay prediction, SCRI, twin simulator)
- FastAPI backend: endpoints for each module, authentication stub, basic logging
- PostgreSQL: core schema populated with synthetic sample data (100 suppliers, 1k orders, 5k shipments)

**What is DEFERRED to Post-Launch:**
- ✗ Bayesian hierarchy for SCRI weights (implement hardcoded, calibrated weights instead)
- ✗ Graph fragility metrics (T(G,t) topology modifier — stub out as constant 1.0)
- ✗ Monte Carlo simulation (deterministic twin with scenario parameter sweeps)
- ✗ Online Bayesian updating from real events (static SCRI computation)
- ✗ Real-event backtesting (validate on synthetic disruption scenarios only)
- ✗ Uncertainty quantification / posterior distributions (point estimates only)
- ✗ AI Copilot (LangChain integration, structured reasoning)
- ✗ Background workers / Celery (all tasks synchronous)
- ✗ Production secrets management (ENV variables only)
- ✗ CI/CD pipelines
- ✗ Comprehensive test suite (smoke tests + core module tests)

### 1.2 MVP Success Criteria

A deployable, portfolio-grade project must demonstrate:
1. **Functional:** all core modules produce predictions/scores end-to-end (no errors, reasonable outputs)
2. **Integrated:** FastAPI ↔ Streamlit ↔ PostgreSQL working seamlessly
3. **Documented:** README, API docs, SCRI methodology explained in dashboard
4. **Reproducible:** fixed random seeds, sample data, Docker stack runnable in <5 minutes
5. **Visual:** SCRI and Twin dashboards are polished and engaging (colors, charts, narrative)
6. **Explainable:** predictions include driver breakdowns and SHAP values (transparency)

---

## PART II: DATA REQUIREMENTS

### 2.1 Required Data (Minimal, Synthetic OK)

For each SCRI component:

#### Delay Prediction
- **Required:**
  - Shipment records: ship_date, expected_delivery, actual_delivery, carrier, region, product_category, lead_time_days
  - Supplier historical: supplier_id, on_time_rate_30d, delay_frequency_30d, leadtime_cv_90d
  - Order context: order_value, quantity
- **Optional:**
  - Port congestion indexes, seasonal indicators, carrier-specific reliability
- **Synthetic Alternative:**
  - Generate 5k shipments using Poisson order arrival, LogNormal lead times, Bernoulli delay (p=0.12 baseline)
  - Create 50 suppliers with varying on_time_rate (0.7–0.95) and lead_time_cv (0.1–0.4)
  - Status: use synthetic for MVP; swap real data in production

#### Supplier Risk Scoring
- **Required:**
  - Supplier-shipment history: delay_rate (delays / total), delivery_variance (std of lead times), concentration (HHI per SKU)
  - Optional: supplier criticality (boolean), region, category
- **Optional:**
  - Financial health proxies, country risk indices, capacity estimates
- **Synthetic Alternative:**
  - Derive from shipment records by aggregating per supplier; compute HHI from volume shares
  - Status: 100% derivable from shipment data; no external source needed

#### SCRI
- **Required:**
  - Aggregated supplier diversity per SKU (HHI), geographic diversity (entropy), lead-time stability (CV), supplier reliability (OTR), inventory buffer (safety_stock / avg_daily_demand)
  - Network metadata: supplier → product → warehouse → region relationships
- **Optional:**
  - Geopolitical risk indexes, supplier financial health
- **Synthetic Alternative:**
  - Compute from shipment + inventory tables; assign network topology via random graph generation
  - Status: 100% from core tables; no special data collection needed

#### Digital Twin
- **Required:**
  - Supplier capacity (volume/month), lead-time distribution (mu, sigma per supplier), inventory settings (safety_stock, reorder_point)
  - Demand profile (daily or weekly mean, seasonality factors)
  - Warehouse capacity, fulfillment SLA targets
- **Optional:**
  - Carrier capacity, failure hazard rates (by region), recovery time distributions
- **Synthetic Alternative:**
  - Derive capacity from historical volume percentiles; fit lead-time distributions empirically
  - Use constant demand or add seasonal pattern (sines/cosines)
  - Status: fully synthetic for MVP; calibrate to real parameters in post-launch

### 2.2 Sample Data Specification (MVP)

**Suppliers:** N=100
- 20 tier-1 (high capacity, low delay rate 0.08)
- 50 tier-2 (medium capacity, mid delay rate 0.12)
- 30 tier-3 (low capacity, high delay rate 0.20)
- Regions: 5 (EMEA, APAC, AMER, LATAM, AFMEA)
- Criticality: 30% single-sourced products, 70% dual/multi-sourced

**Products:** N=50 SKUs
- 10 critical (high revenue, single-sourced)
- 20 standard (medium revenue, dual-sourced)
- 20 commodity (low revenue, multi-sourced)

**Orders:** N=1,000
- Distribution: 70% EMEA, 15% APAC, 10% AMER, 5% others
- Order value: LogNormal(μ=5000, σ=2000)
- Quantity: Poisson(λ=10) per line item

**Shipments:** N=5,000
- Generated by matching orders to suppliers
- Lead time ~ LogNormal(μ=μ_supplier, σ=σ_supplier)
- Delay: Bernoulli(p = p_supplier × (1 + seasonal_factor))
- Simulating 6–12 months of history

**Inventory:** daily snapshots
- 50 products × 5 warehouses = 250 daily snapshots
- Stock levels: uniform(safety_stock, 2×safety_stock)
- Safety stock: 10–30 days of supply depending on product criticality

---

## PART III: FEATURE ENGINEERING PLAN

### 3.1 Delay Prediction Features

**Raw Features (from shipment records):**
- lead_time_days, expected_delivery_date, order_value, product_category, region, carrier
- Day of week, month, quarter

**Derived Features (rolling-window aggregates):**
- Rolling 30-day aggregates:
  - supplier_on_time_rate_30d = count(delays ≤ 0) / total
  - supplier_delay_freq_30d = count(delays > 0) / total
  - supplier_leadtime_mean_30d, supplier_leadtime_std_30d
  - carrier_reliability_30d = same for carrier (not supplier)
  - region_delay_rate_30d
- Rolling 90-day CV:
  - supplier_leadtime_cv_90d = std / mean

**Feature Selection (for modeling):**
Priority 1 (high predictive power, low leakage):
  - supplier_on_time_rate_30d
  - supplier_leadtime_cv_90d
  - carrier_reliability_30d
  - order_value
  - region_delay_rate_30d

Priority 2 (secondary signals):
  - lead_time_days
  - product_category (encoded as target-mean)
  - day_of_week (one-hot)

**Preprocessing:**
- Standardization: z-score normalize all numeric features
- Encoding: one-hot categorical (region, carrier)
- Missing imputation: forward-fill with mean for time-series features

**Output Format:**
- DataFrame [N_samples, 15 features] ready for sklearn pipeline
- Train/test split: 80/20 by date (no leakage)

### 3.2 Supplier Risk Features

**Raw Components:**
- delay_freq: count(delays) / count(shipments) over window (30d, 90d, 365d)
- delivery_variance: var(lead_time_days) — measure of inconsistency
- supply_concentration: HHI per critical SKU (1 - Σ(share_i)^2)
- recent_failure_rate: exponential decay weighting recent delays heavier

**Derived Supplier-Level Metrics:**
- reliability_score = exponentially weighted OTR (recent performance emphasized)
- variance_score = 1 / (1 + CV(lead_time)) — inverse CV, scaled [0,1]
- concentration_score = 1 - mean(HHI) — average across SKUs supplied
- recency_score = fraction of last 30 shipments on-time

**Risk Factor Aggregation (MVP — static weights):**
- Risk = 100 × (0.40 × (1 - reliability) + 0.35 × (1 - variance_score) + 0.25 × (1 - concentration))
- Output: risk_score ∈ [0, 100] where 0=no risk, 100=max risk

**Supplier Risk Output:**
- supplier_id, supplier_name, risk_score, reliability_score, variance_score, concentration_score, confidence (0.5 for MVP — stub)

### 3.3 SCRI Feature Engineering

**Driver Computation (MVP — deterministic, no Bayes):**

1. **Supplier Diversity** $d_1$
   - Per critical SKU: HHI = Σ(supplier_share)^2
   - Driver: d_1 = mean(1 - HHI) over critical SKUs, revenue-weighted
   - Range: [0,1]

2. **Geographic Diversity** $d_2$
   - Share of volume by region (EMEA, APAC, etc.)
   - Driver: d_2 = -Σ P(region) log(P(region)) / log(# regions)
   - Range: [0,1]

3. **Lead-Time Stability** $d_3$
   - CV of lead times over 90-day rolling window
   - Driver: d_3 = 1 / (1 + CV) — capped at [0,1]

4. **Supplier Reliability** $d_4$
   - Revenue-weighted on-time rate (recent 30 days, exponential decay)
   - Driver: d_4 = OTR [0,1]

5. **Inventory Buffer Strength** $d_5$
   - Safety stock / average daily demand (days of supply)
   - Driver: d_5 = min(DOS / target_DOS, 1) where target_DOS = 20 days

**Transform Functions (MVP — simple, learnable later):**
- Linear transforms (stub): φ_i(d_i) = d_i (identity)
- OR logit transforms: φ_i(d_i) = 1 / (1 + exp(-α(d_i - τ))) with fixed (α, τ) per driver
- MVP choice: identity (simplest; enables later refinement)

**Aggregation (MVP — hybrid, no topology):**
- Critical drivers M = {d_1, d_2, d_5} (diversity, geography, buffer)
  - M_core = (φ_1^0.4 × φ_2^0.35 × φ_5^0.25)^(1/1) geometric mean
- Ancillary drivers A = {d_3, d_4} (stability, reliability)
  - A_core = 0.5 × φ_3 + 0.5 × φ_4 arithmetic mean
- Combined: SCRI_raw = M_core^0.6 × (1 + A_core)^0.4 × 1.0 (topology modifier = 1)
- Scaled: SCRI = 100 × (SCRI_raw - min_observed) / (max_observed - min_observed)

**Output:**
- SCRI [0,100], category (Weak/Moderate/Strong/Highly Resilient), driver breakdown table

---

## PART IV: DIGITAL TWIN MVP

### 4.1 Simplified Engine (Deterministic, No Monte Carlo)

**MVP Scope:**
- Single-run scenarios (not 1000-run Monte Carlo — save for v1.1)
- Deterministic lead times (use mean + scenario-specific modifier)
- Deterministic demand (use historical average or linear trend)
- Deterministic inventory policies (fixed reorder point and quantity)

**What Can Be Omitted Initially:**
- ✗ Stochastic lead-time sampling — use supplier_mean_lead_time + modifier
- ✗ Supplier failure duration recovery distributions — use fixed duration
- ✗ Demand seasonality & shocks — use constant or linear trend
- ✗ Network rerouting logic — if one supplier fails, allocate to next-best (simple greedy, not optimization)
- ✗ Port congestion, weather, geopolitical — environmental factors constant
- ✗ Carrier capacity & transport network — treat as abstracted lead-time modifiers

### 4.2 Scenario Types (MVP)

1. **Supplier Failure**
   - Duration: 3, 7, 14 days (user-selectable)
   - Effect: supplier capacity → 0; orders reroute to alternatives at cost
   - Output: revenue loss, fill rate, lead time impact, recovery time

2. **Warehouse Shutdown**
   - Duration: 3, 7 days
   - Effect: warehouse out-of-service; inventory redistributed to alternate warehouse
   - Output: same metrics

3. **Demand Spike**
   - Increase: +20%, +50% (user-selectable)
   - Duration: 7, 14 days
   - Effect: orders increase; inventory depletes faster; may trigger stockouts
   - Output: revenue opportunity, fill rate impact, inventory risk

4. **Transportation Delay**
   - Delay multiplier: 1.5x, 2x lead time
   - Duration: 3, 7 days (affects shipments in transit)
   - Effect: in-transit shipments delayed; warehouse inventory delayed
   - Output: lead time impact, fill rate, order fulfillment SLA breaches

### 4.3 Engine Pseudocode (Not Implementation)

```
Simulation:
  Initialize state:
    inventory[warehouse][product] = current_stock
    scheduled_shipments = list of (product, qty, arrival_time)
    open_orders = list of (product, qty, demand_time)
    cumulative_kpis = {revenue: 0, fill_rate: 0, delays: 0}

  Inject scenario: modify lead_times, remove supplier capacity, spike demand

  For time t in [0, simulation_horizon]:
    # Process arriving shipments
    for shipment in scheduled_shipments:
      if shipment.arrival_time == t:
        inventory[warehouse][product] += shipment.qty
        remove shipment from scheduled_shipments

    # Process open orders (try fulfill)
    for order in open_orders:
      available_qty = inventory[primary_warehouse][order.product]
      if available_qty >= order.qty:
        fulfill from primary_warehouse
        inventory -= order.qty
        revenue += order.value
        fill_rate += 1
      else if alternate_warehouse has stock:
        fulfill from alternate (at higher cost)
      else:
        backorder or lost_sale
        fill_rate += (available_qty / order.qty)
      remove order from open_orders

    # Process replenishment checks (if stock < reorder point)
    for product in inventory:
      if inventory[warehouse][product] < reorder_point[product]:
        place order to supplier (with scenario-modified lead time)
        schedule shipment arrival

  Aggregate KPIs and return impact summary
```

### 4.4 MVP Outputs

Per scenario run:
- **Revenue Impact:** baseline_revenue - scenario_revenue (absolute and %)
- **Fill Rate:** fulfilled_qty / demanded_qty
- **Lead Time Impact:** avg_fulfilled_lead_time - baseline
- **Stockout Events:** count and duration of inventory shortages
- **Recommendation:** narrative summary ("If supplier X fails for 7 days, expect $250k revenue loss and 15% fill-rate drop. Mitigation: increase buffer by 10 days → reduces loss to $80k")

---

## PART V: DATABASE MAPPING

### 5.1 Map SCRI Concepts to Existing Schema

| SCRI Component | Data Source | SQL Query / Aggregation |
|---|---|---|
| supplier_diversity (d_1) | shipments, suppliers | SELECT supplier_id, COUNT(*) as volume FROM shipments WHERE order_date >= NOW() - 30d GROUP BY supplier_id; COMPUTE HHI per product |
| geographic_diversity (d_2) | shipments | SELECT region, COUNT(*) FROM shipments GROUP BY region; COMPUTE entropy |
| leadtime_stability (d_3) | shipments | SELECT supplier_id, STDDEV(transit_time_days) / AVG(transit_time_days) FROM shipments WHERE order_date >= NOW() - 90d GROUP BY supplier_id |
| supplier_reliability (d_4) | shipments | SELECT COUNT(CASE WHEN delayed=1 THEN 1 END)::FLOAT / COUNT(*) as otr FROM shipments WHERE order_date >= NOW() - 30d GROUP BY supplier_id |
| inventory_buffer (d_5) | inventory | SELECT product_id, AVG(safety_stock) / AVG(avg_daily_usage) as dos FROM inventory GROUP BY product_id; REVENUE-WEIGHT |
| supplier_risk_scores | risk_scores table | INSERT new computed scores; query by supplier_id, computed_at |
| scri_scores | risk_scores table (score_type='scri') | INSERT computed SCRI; query by computed_at for time-series |
| simulation_results | simulations table | INSERT scenario runs with scenario_type, payload (JSON), impact_revenue, impact_inventory, etc. |

### 5.2 Schema Extension Needed (Minimal)

**Add to existing schema:**
- `risk_scores.score_type` enum or string ('supplier_risk', 'scri', 'delay_prediction')
- `simulations.scenario_params` JSONB for storing input parameters
- `simulations.impact_metrics` JSONB for storing detailed outputs (per SKU, per region impacts)
- Indexes: `(supplier_id, computed_at)` on risk_scores, `(scenario_type, created_at)` on simulations

**No major schema redesign needed** — current structure (suppliers, shipments, orders, inventory, risk_scores, simulations) is sufficient.

---

## PART VI: API MAPPING

### 6.1 MVP API Endpoints

#### Data Ingestion
- `POST /api/data/upload` — CSV upload, validation, staging (existing; enhance with profiling output)
- `GET /api/data/profile` — return data quality report (NEW; non-blocking for MVP)

#### Analytics & KPIs
- `GET /api/analytics/kpis` — revenue, orders, delay_rate, OTIF, lead_time (NEW; mock data OK)
- `GET /api/analytics/suppliers` — supplier performance leaderboard (NEW)

#### Delay Prediction
- `POST /api/prediction/delay` — input shipment features, return probability + SHAP explanation (NEW; stub → trained model)
- `GET /api/prediction/history` — past predictions and outcomes (NEW; optional for MVP)

#### Supplier Risk
- `GET /api/risk/supplier/{supplier_id}` — risk_score, reliability, variance, concentration (NEW)
- `GET /api/risk/summary` — top-10 risky suppliers, distribution (NEW)

#### SCRI
- `GET /api/resilience/scri` — current SCRI, category, driver breakdown (NEW)
- `GET /api/resilience/scri/history` — time-series SCRI (NEW; optional for MVP)
- `GET /api/resilience/drivers` — detailed breakdown of each driver (NEW)

#### Digital Twin Simulation
- `POST /api/simulation/run` — scenario definition, return impact summary (NEW)
- `GET /api/simulation/results/{simulation_id}` — retrieve stored results (NEW; optional for MVP)

#### Copilot (DEFERRED)
- `POST /api/copilot/query` — defer to v1.1

### 6.2 Response Schema Examples (Conceptual, Not Implementation)

```json
{
  "delay_prediction": {
    "delay_probability": 0.72,
    "predicted_label": "Delayed",
    "model_name": "xgboost-v1",
    "explanation": {
      "supplier_on_time_rate_30d": -0.15,  // negative = increases delay risk
      "supplier_leadtime_cv_90d": 0.12,
      "carrier_reliability_30d": -0.08
    }
  },
  
  "supplier_risk": {
    "supplier_id": 42,
    "supplier_name": "Acme Logistics",
    "risk_score": 78.5,
    "reliability_score": 0.72,
    "variance_score": 0.65,
    "concentration_score": 0.55,
    "confidence": 0.80,
    "recommendations": ["Diversify with Supplier 15", "Increase buffer stock"]
  },
  
  "scri": {
    "scri_score": 65.3,
    "category": "Strong",
    "drivers": {
      "supplier_diversity": 0.68,
      "geographic_diversity": 0.72,
      "leadtime_stability": 0.58,
      "supplier_reliability": 0.75,
      "inventory_buffer": 0.82
    },
    "weighted_contributions": {
      "multiplicative_core": 0.68,
      "additive_core": 0.67,
      "topology_modifier": 1.0
    }
  },
  
  "simulation": {
    "scenario_name": "Supplier Failure (7 days)",
    "supplier_id": 42,
    "duration_days": 7,
    "revenue_impact": -145000,
    "revenue_impact_pct": -3.2,
    "fill_rate_impact": -0.08,
    "lead_time_impact_days": 2.3,
    "recovery_time_days": 5,
    "summary": "If Supplier 42 fails for 7 days, expect $145k revenue loss and 8% fill-rate drop."
  }
}
```

---

## PART VII: DASHBOARD MAPPING

### 7.1 Executive Dashboard (Landing Page)

**KPI Cards (4–6 metrics):**
- Revenue (YTD, target %, trend)
- Orders (YTD, MoM %)
- Delay Rate (%, target)
- On-Time In-Full (OTIF %)
- SCRI (0–100, category, trend icon)
- Supply Chain Health (narrative summary, 1–2 sentences)

**Charts:**
- Revenue trend (30d, weekly bars with trend line)
- Orders by region (pie or bar)
- Delay rate trend (line, with control limit bands)
- Top 3 risky suppliers (horizontal bar, risk_score)
- SCRI time-series (line, with target band)

**Actions:**
- Button: "Explore SCRI Drivers" → link to SCRI Dashboard
- Button: "View Risky Suppliers" → link to Supplier Intelligence
- Button: "Run Simulation" → link to Twin Dashboard

### 7.2 SCRI Dashboard (Dedicated Page)

**Headline:**
- SCRI score (large, colored gauge: 0–40=Red, 40–60=Yellow, 60–80=Green, 80–100=Dark Green)
- Category label (Weak / Moderate / Strong / Highly Resilient)
- Trend (↑ +3.2 pts this week)

**Driver Breakdown:**
- 5 horizontal bar charts, one per driver (0–100 scale, same color coding)
- Labels: Supplier Diversity (68), Geographic Diversity (72), Lead-Time Stability (58), Supplier Reliability (75), Inventory Buffer (82)

**Table: Driver Details**
- Driver name, score, interpretation, recommendation
- Example: "Geographic Diversity (72/100) — Supply is spread across 4 regions but concentrated in EMEA (60% share). Recommendation: develop suppliers in APAC."

**Interactive:**
- Slider to simulate driver changes (e.g., "If we double buffer stock..."); SCRI updates in real-time
- Scenario buttons: "What if we onboard Supplier XYZ?" (triggers SCRI recomputation)

**Bottom Section: Recommendations**
- Ordered by expected ΔSCRI improvement
- Example: "[+8 pts] Increase safety stock on SKU-001 from 15→20 days" "[+5 pts] Onboard alternative supplier for Product-A"

### 7.3 Digital Twin Simulator Dashboard

**Inputs Panel (Left Sidebar):**
- Scenario type: dropdown (Supplier Failure, Warehouse Shutdown, Demand Spike, Transport Delay)
- Scenario parameters: duration (days), intensity (multiplier for demand/delay)
- Supplier/product/region: multi-select or single-select

**Run Button & Progress:**
- "Run Simulation" button (triggers POST /api/simulation/run)
- Progress indicator (running... 0–100% — mock for MVP since deterministic)

**Output Panel (Main):**
- Summary cards (4 metrics):
  - Revenue Impact: $X (Red if negative, Green if positive)
  - Fill Rate: X% (with target band)
  - Lead Time: +X days (Red if high)
  - Recovery Time: X days

**Narrative Summary:**
- 2–3 sentences auto-generated from impact values
- Example: "If Supplier Acme fails for 7 days, revenue drops ~$150k (2.1% of weekly baseline) and fill rate dips to 88% (target: 95%). Full recovery within 5 days."

**Comparison View (Optional):**
- Side-by-side impact for two scenarios (e.g., "3-day failure vs 7-day failure")

**Drill-Down (Optional for MVP):**
- Time-series chart showing KPIs over simulation horizon (if deterministic run shows time-stepped trajectory)

### 7.4 Supplier Intelligence Dashboard

**Leaderboard Table:**
- Columns: Supplier Name, Risk Score, Reliability, Variance, Concentration, Confidence, Actions
- Sorting: by Risk Score (descending = most risky first)
- Filters: Region, Category, Risk Tier (High/Medium/Low)

**Risk Heatmap (Optional):**
- Grid: Suppliers (rows) × Risk Dimensions (columns: Reliability, Variance, Concentration)
- Color intensity = score (red = high risk)

**Supplier Detail Modal (Click on Supplier):**
- Risk factors breakdown (pie or bar)
- Recommendation list (from API)
- Recent shipment history (5 most recent with delay status)

**Distribution Charts:**
- Histogram: risk_score distribution (with mean, median, quartiles)
- Scatter: reliability vs variance (bubble size = volume)

### 7.5 Delay Prediction Page

**Scoring Form:**
- Input fields: supplier_id, product_id, region, lead_time_days, order_value, previous_delay_rate, carrier_reliability
- "Predict" button → calls POST /api/prediction/delay

**Output:**
- Large gauge: delay_probability (0–100%)
- Label: "Delayed" (if >50%) or "On-Time" (if ≤50%)
- Model confidence indicator

**Explainability:**
- SHAP waterfall chart or feature importance bar
- Table: Feature, Value, Contribution (positive/negative)

**Batch Scoring (Optional for MVP):**
- File upload for CSV of shipments
- Download results as CSV with predictions + explanations

---

## PART VIII: DEVELOPMENT ROADMAP (Week-by-Week)

### Week 1: Foundation & Setup
**Days 1–2: Project Setup**
- Initialize repo, branch strategy, local dev environment
- Set up Docker Compose with PostgreSQL, FastAPI, Streamlit containers
- Generate synthetic sample data (5k shipments, 100 suppliers, etc.)
- Load sample data into PostgreSQL
- Status check: `docker compose up` runs without errors

**Days 3–4: Data Pipeline**
- Build data loading script (CSV → PostgreSQL; schema validation)
- Create rolling-window feature computation (delay_rate_30d, leadtime_cv_90d, etc.)
- Implement feature store as views or materialized tables
- Test: queries return correct aggregates for known suppliers

**Days 5: Analytics API Skeleton**
- Implement GET /api/analytics/kpis (mock data, not from DB initially)
- Implement GET /api/analytics/suppliers (mock leaderboard)
- Test: FastAPI docs at /docs work; responses valid JSON

**Deliverable:** Working Docker stack, PostgreSQL with sample data, FastAPI running with analytics endpoints returning mock data.

---

### Week 2: Delay Prediction Module
**Days 1–2: Feature Engineering & Modeling**
- Extract features from shipment records (train_set = shipments from month 1–5, test = month 6)
- Train Logistic Regression baseline (sklearn)
- Train XGBoost model (xgboost library)
- Compute metrics: ROC-AUC, Precision@0.5, Calibration
- Save models to disk (joblib)

**Days 3–4: SHAP Explainability**
- Load trained XGBoost model
- Compute SHAP values for sample predictions
- Create explainability function that returns top-3 driver influences per prediction

**Day 5: API Integration**
- Implement POST /api/prediction/delay endpoint
- Load model at startup; serve predictions with <200ms latency
- Test: sample shipment payload returns probability + explanation

**Deliverable:** Trained delay models, SHAP explainability working, API endpoint functional.

---

### Week 3: Supplier Risk & SCRI Modules
**Days 1–2: Supplier Risk Computation**
- Build risk computation logic (delay_freq, variance, concentration scores)
- Aggregate into risk_score with static weights (0.4, 0.35, 0.25)
- Implement GET /api/risk/supplier/{id} endpoint
- Populate risk_scores table via batch job

**Days 3–4: SCRI Computation**
- Extract driver values: d_1 (diversity), d_2 (geo), d_3 (stability), d_4 (reliability), d_5 (buffer)
- Implement aggregation: M_core (geometric), A_core (arithmetic), topology modifier (=1), final scaling
- Store SCRI results in risk_scores table (score_type='scri')
- Implement GET /api/resilience/scri endpoint with driver breakdown

**Day 5: Validation**
- Spot-check SCRI calculations (verify formulas, value ranges [0-100])
- Validate driver contributions (e.g., single-sourced supplier should lower SCRI)
- Test: SCRI dashboard page loads without errors

**Deliverable:** Supplier Risk API, SCRI computed and exposed via endpoint, preliminary validation.

---

### Week 4: Digital Twin MVP
**Days 1–2: Twin Engine (Deterministic)**
- Build scenario runner for 4 types (supplier failure, warehouse shutdown, demand spike, transport delay)
- Implement deterministic simulation (no Monte Carlo): use fixed lead times, no randomness
- Compute impact metrics (revenue_loss, fill_rate, lead_time_impact)
- Test: "Supplier 42 fails for 7 days" produces reasonable output

**Days 3–4: Twin API & Storage**
- Implement POST /api/simulation/run endpoint
- Store results in simulations table
- Implement GET /api/simulation/results/{id}
- Test: API accepts scenario parameters, returns impact summary

**Day 5: Twin Dashboard**
- Build Streamlit twin simulator page
- Form inputs for scenario parameters
- Display summary cards and narrative
- Test: form submission → API call → results displayed

**Deliverable:** Deterministic Digital Twin operational, API endpoint live, dashboard page functional.

---

### Week 5: Streamlit Dashboard Integration
**Days 1–2: Executive Dashboard**
- Build KPI cards (revenue, orders, delay_rate, OTIF, SCRI)
- Add charts (revenue trend, orders by region, delay rate, risky suppliers)
- Integrate API calls to fetch live data
- Style and polish UI (colors, fonts, spacing)

**Days 3–4: SCRI & Supplier Risk Pages**
- SCRI page: driver breakdown, interactive sliders, recommendations
- Supplier Intelligence page: leaderboard table, filters, risk heatmap
- Delay Prediction page: scoring form, results display, explainability

**Day 5: Testing & Polish**
- End-to-end test: navigate all pages, verify data refreshes
- UX refinement: responsive layout, mobile-friendly (if applicable)
- Performance check: page load time <3s

**Deliverable:** Complete Streamlit dashboard, all pages functional, integrated with APIs.

---

### Week 6: Testing & Validation
**Days 1–2: Unit Tests**
- Write tests for feature engineering (verify aggregations)
- Write tests for delay prediction (model outputs in expected range, SHAP shapes correct)
- Write tests for SCRI logic (driver values [0-1], final SCRI [0-100])
- Target: ≥50 test cases covering happy path + edge cases

**Days 3–4: Integration Tests**
- Test end-to-end flows: upload data → compute features → predict → display on dashboard
- Test API error handling (invalid inputs, missing data)
- Load testing: ensure <200ms API latency under reasonable load

**Day 5: Documentation & README**
- Write README with setup instructions (Docker, sample data, quickstart)
- Document API endpoints (request/response examples)
- Add SCRI methodology explanation (simple summary in dashboard or docs)
- Update CONTRIBUTING guide for future developers

**Deliverable:** Test suite (unit + integration), comprehensive README, project ready for portfolio review.

---

### Week 7–8 (Buffer): Final Polish & Deployment Prep
**Buffer for:**
- Bug fixes from testing
- Performance tuning (if needed)
- UI polish (colors, typography, layout refinement)
- Data visualization improvements (better charts, legends)
- Docker image optimization
- Deployment documentation (how to run on cloud)

**Deployment Checklist:**
- [ ] All tests pass
- [ ] No hardcoded credentials (use ENV)
- [ ] API rate limiting stub in place
- [ ] Logging captures key events
- [ ] Health check endpoint `/health` returns 200 OK
- [ ] Sample data loadable in <1 min
- [ ] Dashboard loads in <3s
- [ ] README complete with 5-min quickstart
- [ ] GitHub repo ready (README, license, .gitignore, etc.)

---

## PART IX: RISK ANALYSIS

### 9.1 Technical Risks (Likelihood, Impact, Mitigation)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Synthetic data doesn't reflect real patterns; SCRI/twin outputs nonsensical | Medium | High | Validate on real case studies from literature; do sensitivity analysis; document assumptions |
| Feature engineering bugs (wrong aggregations, data leakage) | Medium | High | Peer review feature code; unit test aggregation functions; audit rolling windows |
| PostgreSQL queries too slow for dashboards | Low | Medium | Add indexes on key columns; use materialized views for heavy aggregations; monitor query plans |
| Digital Twin deterministic approach doesn't capture variability; claims seen as "naive" | Medium | High | Acknowledge MVP simplification explicitly; plan Monte Carlo for v1.1; show stochastic sensitivity analysis in sensitivity section |
| Streamlit performance degrades with dataset size | Low | Medium | Cache API responses client-side; lazy-load charts; use session state to avoid recomputation |
| Delay prediction model overfits on small synthetic dataset | Medium | Medium | Use cross-validation; track validation metrics; implement regularization (L1/L2); keep baseline (LogReg) for comparison |
| SCRI weights are arbitrary (equal-weight aggregation); reviewers say "not principled" | High | High | Pre-empt by labeling as "MVP v1.0, weights equal-weight baseline; v1.1 will learn weights from twin calibration" |

### 9.2 Project Risks (Scope Creep, Timeline)

| Risk | Mitigation |
|------|-----------|
| Pressure to add AI Copilot to MVP | Defer explicitly to v1.1; document in GitHub issues; mention in README roadmap |
| Requirement for real-event validation data emerges mid-project | Clarify upfront: MVP uses synthetic data; offer to integrate real case study post-launch |
| Team wants production-grade Bayesian SCRI upfront | Negotiate: start with static weights (v1.0), evolve to Bayesian (v1.1); explain time tradeoff |
| Data quality issues discovered late | Start with synthetic data (controlled); plan real-data integration pathway; add data quality checks early |

### 9.3 Hardest Parts (Likely to Fail / Need Most Attention)

1. **Feature Engineering for Delay Prediction**
   - Challenge: rolling windows must avoid data leakage; feature staleness on test set
   - Risk: model seems to work on train but fails on future data
   - Mitigation: rigid time-based validation; audit lag structures; ablation tests

2. **SCRI Interpretation & Justification**
   - Challenge: static weights chosen arbitrarily; no strong empirical justification for v1.0
   - Risk: reviewers/stakeholders dismiss as "just a weighted sum"
   - Mitigation: be explicit about MVP status; show v1.0 as baseline for v1.1 Bayesian calibration; document methodology trade-offs

3. **Digital Twin Calibration**
   - Challenge: assume stationarity (lead times, failure rates) which may not hold
   - Risk: simulated impacts misaligned with reality; twin deemed "useless"
   - Mitigation: validate twin on historical events; show sensitivity to parameter changes; build explainability into outputs

4. **Dashboard UX**
   - Challenge: fitting 5 drivers + KPIs + recommendations into intuitive UI
   - Risk: dashboard cluttered, confusing, slow
   - Mitigation: iterate wireframes early; prioritize ruthlessly (what's essential vs nice-to-have); test with users

5. **PostgreSQL-Streamlit Performance**
   - Challenge: large shipment tables (5k records for MVP; real data could be 500k+) → slow dashboard loads
   - Risk: dashboard feels sluggish; poor user experience
   - Mitigation: add indexes, use caching, pre-compute aggregates, profile early

---

## PART X: MVP ARCHITECTURE (Final Version 1.0)

### 10.1 Component Diagram (Textual)

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Streamlit)                      │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  Executive   │     SCRI     │   Suppliers  │   Twin       │  │
│  │  Dashboard   │   Dashboard  │ Intelligence │  Simulator   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                             ↓ (HTTP calls)
┌─────────────────────────────────────────────────────────────────┐
│                      BACKEND (FastAPI)                           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  Analytics   │   Risk &     │  Prediction  │   Simulation │  │
│  │  Endpoints   │   SCRI       │  Endpoints   │  Endpoints   │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Services: ETL, Analytics, Risk Scoring, SCRI Calc,     │   │
│  │  Delay Prediction, Twin Engine, Explainability          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                             ↓ (SQL queries)
┌─────────────────────────────────────────────────────────────────┐
│                  DATABASE (PostgreSQL)                           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐  │
│  │  suppliers   │  shipments   │  orders      │  inventory   │  │
│  │  products    │  risk_scores │  simulations │              │  │
│  └──────────────┴──────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 10.2 Data Flow Example: Executive Dashboard Load

```
1. User opens Streamlit dashboard
2. Dashboard queries (parallel):
   - GET /api/analytics/kpis → retrieves revenue, orders, delay_rate, OTIF, lead_time
   - GET /api/resilience/scri → retrieves SCRI score, category, drivers
   - GET /api/risk/summary → retrieves top-10 risky suppliers
3. Backend services:
   - AnalyticsService queries PostgreSQL; aggregates shipments, orders into KPIs
   - SCRIService computes drivers from shipment aggregates; applies SCRI formula
   - RiskService queries risk_scores table; returns top 10 by risk_score
4. FastAPI returns JSON responses
5. Streamlit renders KPI cards, charts, and recommendations
6. User can click "Explore SCRI" → navigates to SCRI Dashboard
   - Loads full driver breakdown, interactive sliders, recommendations
```

### 10.3 File Structure (By End of Week 6)

```
SupplyChainIQ/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── main.py (FastAPI app, router registration)
│   │   ├── routes/
│   │   │   ├── analytics.py (KPI endpoints)
│   │   │   ├── prediction.py (delay prediction)
│   │   │   ├── risk.py (supplier risk)
│   │   │   ├── resilience.py (SCRI)
│   │   │   ├── simulation.py (Digital Twin)
│   │   ├── schemas/
│   │   │   ├── analytics.py
│   │   │   ├── prediction.py
│   │   │   ├── risk.py
│   │   │   ├── resilience.py
│   │   │   ├── simulation.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   ├── services/
│   │   ├── etl.py (data loading)
│   │   ├── analytics.py (KPI aggregation)
│   │   ├── prediction.py (delay prediction inference)
│   │   ├── risk.py (supplier risk scoring)
│   │   ├── resilience.py (SCRI computation)
│   │   ├── simulation.py (Digital Twin engine)
│   ├── models/
│   │   ├── trainer.py (training pipeline)
│   │   ├── explainability.py (SHAP)
│   │   ├── model_registry.py
│   ├── db/
│   │   ├── schemas.sql
│   ├── streamlit_app/
│   │   ├── app.py (launcher)
│   │   ├── pages/
│   │   │   ├── executive_dashboard.py
│   │   │   ├── scri_dashboard.py
│   │   │   ├── supplier_intelligence.py
│   │   │   ├── delay_prediction.py
│   │   │   ├── digital_twin.py
├── data/
│   ├── raw/ (sample CSV)
│   ├── processed/ (feature store)
│   ├── models/ (trained models, SHAP explainers)
├── tests/
│   ├── test_api.py
│   ├── test_services.py (feature engineering, risk, SCRI, twin)
├── docs/
│   ├── architecture.md
│   ├── SCRI_v2_Research_Design.md
│   ├── api_design.md
│   ├── sprint_plan.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md (setup, quickstart, roadmap)
├── .env.example
├── .gitignore
```

### 10.4 Deployment Checklist (Ready for Portfolio)

- [ ] Docker `docker compose up` brings up db, API, dashboard in <2 min
- [ ] Sample data loads automatically on container start
- [ ] FastAPI docs at http://localhost:8000/docs shows all endpoints
- [ ] Streamlit dashboard loads at http://localhost:8501 without errors
- [ ] All KPI metrics display with reasonable values
- [ ] SCRI score is between 0–100 with driver breakdown visible
- [ ] Delay prediction form accepts inputs and returns probability + explanation
- [ ] Supplier risk leaderboard shows ≥20 suppliers ranked by risk
- [ ] Digital Twin simulation runs and shows impact summary within 5s
- [ ] No hardcoded passwords/secrets in code (all ENV-based)
- [ ] Tests pass: `pytest tests/` runs 50+ tests with >80% passing
- [ ] README includes: project overview, setup instructions, architecture diagram, API endpoints, SCRI methodology summary, roadmap
- [ ] GitHub repo is clean: no generated files, proper .gitignore, clear commit history
- [ ] Code follows style guide: consistent naming, docstrings on key functions, type hints where practical

---

## PART XI: SUCCESS METRICS (How We Know MVP is Done)

1. **Functional Completeness:**
   - ✓ All 5 core modules (analytics, delay pred, risk, SCRI, twin) produce outputs end-to-end
   - ✓ Dashboard renders all pages without crashes
   - ✓ API endpoints respond with valid JSON, <500ms latency

2. **Data Quality:**
   - ✓ Sample data represents realistic supply chain (100+ suppliers, diverse lead times, some delays)
   - ✓ Feature aggregations (rolling windows, diversity indices) validated spot-checks
   - ✓ SCRI driver values reasonable ([0-1] range, sensitivity to data changes)

3. **Explainability:**
   - ✓ SHAP values provided for delay predictions (interpretable feature impacts)
   - ✓ SCRI driver breakdown visible and actionable
   - ✓ Recommendations generated from driver/risk analysis

4. **Portfolio Value:**
   - ✓ Project demonstrates: SQL, data engineering, ML (training + serving), analytics, API design, UI/UX, Docker
   - ✓ Code is clean, documented, and deployable (not a one-off script)
   - ✓ Narrative is clear: "I built a supply chain resilience index and simulation engine"

5. **Research Grounding:**
   - ✓ SCRI methodology documented (drivers, aggregation, formula) in README or dashboard
   - ✓ Digital Twin logic documented (entities, scenarios, impact calculations)
   - ✓ Future work (Bayesian weights, Monte Carlo, graph topology) mapped out

---

## SUMMARY: 6–8 Week MVP Execution Plan

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Foundation & Setup | Docker stack, sample data, analytics stubs |
| 2 | Delay Prediction | Trained models, SHAP explainability, API working |
| 3 | Risk & SCRI | Supplier risk API, SCRI computed and validated |
| 4 | Digital Twin | Deterministic twin engine, simulator API, dashboard |
| 5 | Streamlit UI | Full dashboard, all pages integrated with APIs |
| 6 | Testing & Docs | Unit/integration tests, README, API docs, validation |
| 7–8 | Buffer & Polish | Bug fixes, UI refinement, final deployment prep |

**Expected Outcome:** A working, deployable SupplyChainIQ v1.0 project that demonstrates supply chain analytics, resilience metrics, and simulation capabilities. Ready for portfolio review, GitHub showcase, and foundation for v1.1 (Bayesian SCRI, Monte Carlo twin, AI Copilot, real-event validation).

