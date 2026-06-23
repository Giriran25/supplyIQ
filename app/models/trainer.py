from __future__ import annotations

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split


class ModelTrainer:
    def __init__(self) -> None:
        self.model = None

    def train_delay_models(self, dataset: pd.DataFrame) -> dict[str, dict[str, float]]:
        features = [
            "lead_time_days",
            "order_value",
            "previous_delay_rate",
            "carrier_reliability",
        ]
        X = dataset[features]
        y = dataset["delayed"].astype(int)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        baseline = LogisticRegression(max_iter=500)
        baseline.fit(X_train, y_train)
        xgb = GradientBoostingClassifier(random_state=42)
        xgb.fit(X_train, y_train)

        metrics = {
            "logistic_accuracy": accuracy_score(y_test, baseline.predict(X_test)),
            "xgboost_accuracy": accuracy_score(y_test, xgb.predict(X_test)),
            "xgboost_f1": f1_score(y_test, xgb.predict(X_test)),
            "xgboost_precision": precision_score(y_test, xgb.predict(X_test)),
            "xgboost_recall": recall_score(y_test, xgb.predict(X_test)),
        }
        self.model = xgb
        return metrics
