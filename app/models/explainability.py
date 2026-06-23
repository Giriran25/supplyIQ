from __future__ import annotations

import shap
import pandas as pd


class ExplainabilityService:
    def __init__(self) -> None:
        self.explainer = None

    def train_explainer(self, model, X: pd.DataFrame) -> None:
        self.explainer = shap.Explainer(model, X)

    def explain(self, X: pd.DataFrame) -> list[dict[str, float]]:
        if self.explainer is None:
            raise RuntimeError("Explainer has not been trained")
        shap_values = self.explainer(X)
        return [dict(zip(X.columns, row.values.tolist())) for row in shap_values.values]
