from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

import pandas as pd


def parse_date(value: str) -> pd.Timestamp:
    return pd.to_datetime(value).normalize()


def ensure_datetime(df: pd.DataFrame, col: str = "date") -> pd.DataFrame:
    df = df.copy()
    df[col] = pd.to_datetime(df[col]).dt.normalize()
    return df


def infer_trading_calendar(dates: Iterable[pd.Timestamp]) -> List[pd.Timestamp]:
    # Simple calendar based on observed dates
    return sorted(pd.to_datetime(list(set(dates))).normalize())
