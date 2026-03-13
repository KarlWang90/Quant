from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

import joblib
import numpy as np
import pandas as pd

from quant.models.baseline_gbdt import predict_gbdt, train_gbdt


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


def predict_model(model: Any, df: pd.DataFrame, model_cfg: Dict[str, Any]) -> pd.DataFrame:
    model_type = model_cfg.get("type", "gbdt")
    if model_type == "gbdt":
        return predict_gbdt(model, df)
    raise ValueError(f"Unsupported model type: {model_type}")


def walk_forward_train_and_predict(
    df: pd.DataFrame,
    model_cfg: Dict[str, Any],
    target: str,
    min_train_dates: int = 60,
    retrain_every_n_dates: int = 20,
) -> ModelResult:
    if df.empty:
        out = df.copy()
        out["pred_return"] = np.nan
        return ModelResult(model=out, metrics={"rmse_oos": None, "prediction_rows": 0})

    ordered = df.sort_values(["date", "ticker"]).reset_index(drop=True)
    unique_dates = list(pd.Index(sorted(pd.to_datetime(ordered["date"]).dropna().unique())))
    if len(unique_dates) <= 1:
        raise ValueError("Walk-forward validation requires at least two distinct trading dates.")

    if min_train_dates >= len(unique_dates):
        min_train_dates = max(1, len(unique_dates) - 1)

    frames: list[pd.DataFrame] = []
    rmse_values: list[float] = []
    current_model: Any | None = None

    for idx, current_date in enumerate(unique_dates):
        current_rows = ordered[ordered["date"] == current_date].copy()
        if idx < min_train_dates:
            current_rows["pred_return"] = np.nan
            frames.append(current_rows)
            continue

        if current_model is None or (idx - min_train_dates) % retrain_every_n_dates == 0:
            train_rows = ordered[ordered["date"] < current_date].dropna(subset=[target])
            if train_rows.empty:
                current_rows["pred_return"] = np.nan
                frames.append(current_rows)
                continue
            current_model = train_model(train_rows, model_cfg, target).model

        scored_rows = predict_model(current_model, current_rows, model_cfg)
        eval_rows = scored_rows.dropna(subset=[target])
        if not eval_rows.empty:
            rmse = float(np.sqrt(((eval_rows["pred_return"] - eval_rows[target]) ** 2).mean()))
            rmse_values.append(rmse)
        frames.append(scored_rows)

    scored = pd.concat(frames, ignore_index=True)
    prediction_rows = int(scored["pred_return"].notna().sum())
    metrics = {
        "rmse_oos": float(np.mean(rmse_values)) if rmse_values else None,
        "prediction_rows": prediction_rows,
        "prediction_dates": int(sum(frame["pred_return"].notna().any() for frame in frames)),
        "min_train_dates": int(min_train_dates),
        "retrain_every_n_dates": int(retrain_every_n_dates),
    }
    return ModelResult(model=scored, metrics=metrics)


def save_model(model: Any, path: str) -> None:
    joblib.dump(model, path)
