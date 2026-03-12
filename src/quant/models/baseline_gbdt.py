from __future__ import annotations

from typing import List, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_squared_error


FEATURE_COLUMNS = [
    "ret_1d",
    "ret_5d",
    "vol_5d",
    "ma_gap",
    "vol_chg",
    "market_ret_1d",
    "news_score",
    "rdagent_score",
    "pe_ttm",
    "pb",
    "roe",
]


def _ensure_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in FEATURE_COLUMNS:
        if col not in out.columns:
            out[col] = 0.0
    return out


def train_gbdt(
    df: pd.DataFrame,
    target_col: str = "forward_return",
    params: dict | None = None,
) -> Tuple[GradientBoostingRegressor, float]:
    params = params or {}
    df = _ensure_features(df)
    df = df.dropna(subset=[target_col])

    X = df[FEATURE_COLUMNS].fillna(0.0)
    y = df[target_col]

    model = GradientBoostingRegressor(**params)
    model.fit(X, y)
    pred = model.predict(X)
    rmse = float(np.sqrt(mean_squared_error(y, pred)))
    return model, rmse


def predict_gbdt(model: GradientBoostingRegressor, df: pd.DataFrame) -> pd.DataFrame:
    df = _ensure_features(df)
    out = df.copy()
    out["pred_return"] = model.predict(out[FEATURE_COLUMNS].fillna(0.0))
    return out
