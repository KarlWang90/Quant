from __future__ import annotations

import pandas as pd


def apply_constraints(
    signals: pd.DataFrame,
    context_df: pd.DataFrame | None = None,
    max_positions: int = 15,
    min_avg_turnover_20d: float = 0.0,
    allow_suspended: bool = False,
) -> pd.DataFrame:
    if signals.empty:
        return signals
    out = signals.copy()
    if context_df is not None and not context_df.empty:
        join_cols = ["date", "ticker", "market"]
        keep_cols = [
            col
            for col in ["avg_turnover_20d", "is_suspended", "close", "volume"]
            if col in context_df.columns
        ]
        if keep_cols:
            out = out.merge(
                context_df[join_cols + keep_cols],
                on=join_cols,
                how="left",
            )

    if min_avg_turnover_20d > 0 and "avg_turnover_20d" in out.columns:
        out = out[out["avg_turnover_20d"].fillna(0) >= min_avg_turnover_20d]

    if not allow_suspended and "is_suspended" in out.columns:
        out = out[~out["is_suspended"].fillna(False)]

    out = out.groupby("date").head(max_positions).reset_index(drop=True)
    return out
