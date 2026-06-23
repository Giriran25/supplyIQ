# Machine Learning Architecture

## Training Pipeline

1. Data ingestion from PostgreSQL into training DataFrames.
2. Feature engineering for delay prediction and risk scoring.
3. Train baseline Logistic Regression and XGBoost classifier.
4. Evaluate using accuracy, precision, recall, F1, ROC-AUC.
5. Persist models and metadata to local registry.

## Feature Engineering

- Shipment features: `lead_time_days`, `transit_time_days`, `expected_vs_actual_gap`
- Supplier performance: `delay_frequency`, `delivery_variance`, `on_time_rate`
- Product mix: `product_category`, `unit_price`, `order_value`
- Region features: `region_delay_rate`, `regional_avg_lead_time`
- Inventory signals: `safety_stock_ratio`, `buffer_strength`
- Supplier risk: `historical_performance`, `reliability_score`

## Model Registry Strategy

- Use a local model registry module in `app/models/model_registry.py`.
- Track `model_name`, `version`, `training_date`, `metrics`, `feature_list`, and `artifact_path`.
- Store serialized model objects in `models/` or a dedicated artifact path.
- Use semantic versioning: `delay-xgb-v1.0.0`, `delay-logreg-v1.0.0`.

## Evaluation Pipeline

- Split dataset into train/validation/test partitions.
- Measure classification metrics on the test set.
- Generate SHAP explainability reports for XGBoost.
- Compare baseline logistic regression to XGBoost on business KPIs.

## Explainable AI

- Use SHAP to compute feature contributions for predicted delay probability.
- Provide explanations for supplier risk score drivers.
- Expose explanations in API payloads and Streamlit visuals.

## Production Considerations

- Keep preprocessing and inference logic consistent between training and serving.
- Validate incoming payload schema before scoring.
- Log inference requests, model version, and prediction latency.
- Support model refresh with retraining after major data updates.
