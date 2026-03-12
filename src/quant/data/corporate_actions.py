from __future__ import annotations

import pandas as pd


def apply_adjustments(df: pd.DataFrame) -> pd.DataFrame:
    """Apply adjustment factor if available (qfq-like)."""
    if df.empty:
        return df
    if "adj_factor" not in df.columns:
        return df
    df = df.copy()
    for col in ["open", "high", "low", "close"]:
        if col in df.columns:
            df[col] = df[col] * df["adj_factor"]
    return df
