from __future__ import annotations

import pandas as pd


def data_quality_report(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"rows": 0, "missing_ratio": 0}
    missing_ratio = float(df.isna().mean().mean())
    return {"rows": int(df.shape[0]), "missing_ratio": missing_ratio}
