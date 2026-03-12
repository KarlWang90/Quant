from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import joblib
import pandas as pd

from quant.models.baseline_gbdt import train_gbdt


@dataclass
class ModelResult:
    model: Any
    metrics: Dict[str, Any]


def train_model(df: pd.DataFrame, model_cfg: Dict[str, Any], target: str) -> ModelResult:
    model_type = model_cfg.get("type", "gbdt")
    params = model_cfg.get("params", {})

    if model_type == "gbdt":
        model, rmse = train_gbdt(df, target_col=target, params=params)
        return ModelResult(model=model, metrics={"rmse": rmse})

    raise ValueError(f"Unsupported model type: {model_type}")


def save_model(model: Any, path: str) -> None:
    joblib.dump(model, path)
