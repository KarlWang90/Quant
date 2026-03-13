from __future__ import annotations

import pandas as pd


def build_signals(df: pd.DataFrame, score_col: str = "pred_return", top_k: int = 10, min_score: float = 0.0) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    out = out.dropna(subset=[score_col])
    out = out[out[score_col] >= min_score]
    out = out.sort_values(["date", score_col], ascending=[True, False])
    out = out.groupby("date").head(top_k).reset_index(drop=True)
    out["signal"] = "BUY"
    return out[["date", "ticker", "market", score_col, "signal"]]
