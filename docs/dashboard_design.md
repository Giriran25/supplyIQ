# Dashboard Design

## Executive Dashboard

- KPI cards: Revenue, Orders, Delay Rate, On-Time Delivery, Average Lead Time
- Trend charts: weekly performance, delay trend, revenue by region
- Summary cards: top risky suppliers, SCRI category, current resilience drivers
- Executive insights panel with narrative highlights

## Supplier Intelligence

- Supplier leaderboard by risk score and reliability
- Risk factor breakdown: delay frequency, delivery variance, historical performance
- Supplier detail view with SHAP explanation of risk score drivers
- Filter by region, category, risk tier

## Delay Prediction

- Interactive form for shipment scenario scoring
- Delay probability gauge and class label
- Pathway analysis for on-time vs delayed scenarios
- SHAP waterfall / feature importance visualization

## SCRI Dashboard

- SCRI score gauge and category bands: Weak, Moderate, Strong, Highly Resilient
- Driver breakdown bar chart: Supplier Diversity, Geographic Diversity, Lead Time Stability, Supplier Reliability, Inventory Buffer Strength
- Score composition table and improvement recommendations

## Digital Twin Simulation

- Scenario selection: Supplier Failure, Demand Spike, Warehouse Shutdown, Transportation Delay
- Inputs: supplier, product, region, impact horizon
- Outputs: revenue impact, inventory impact, delay impact, service impact
- Scenario summary and risk mitigation guidance

## AI Copilot

- Query box for natural-language executive questions
- Answer panel with supporting metrics and suggested actions
- Quick prompts: "Why is supplier X risky?", "What happens if supplier A fails?", "Explain SCRI score"
- Contextual cards linking to analytics views and simulation results
