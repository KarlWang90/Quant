from __future__ import annotations

import pandas as pd


def build_orders(signals: pd.DataFrame) -> pd.DataFrame:
    if signals.empty:
        return signals
    out = signals.copy()
    out["order_type"] = "BUY"
    out["reason"] = "Model score ranked"
    return out
