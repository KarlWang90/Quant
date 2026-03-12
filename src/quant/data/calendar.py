from __future__ import annotations

from typing import List

import pandas as pd


def infer_calendar(df: pd.DataFrame) -> List[pd.Timestamp]:
    if df.empty or "date" not in df.columns:
        return []
    dates = pd.to_datetime(df["date"]).dt.normalize().unique()
    return sorted(dates)
