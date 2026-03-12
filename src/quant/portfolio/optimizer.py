from __future__ import annotations

import pandas as pd


def equal_weight(signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return signals
    out = signals.copy()
    out["weight"] = 1.0 / out.groupby("date")["ticker"].transform("count")
    return out
