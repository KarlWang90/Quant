from __future__ import annotations

import pandas as pd


def apply_constraints(signals: pd.DataFrame, max_positions: int = 15) -> pd.DataFrame:
    if signals.empty:
        return signals
    out = signals.copy()
    out = out.groupby("date").head(max_positions).reset_index(drop=True)
    return out
