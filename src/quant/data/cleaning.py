from __future__ import annotations

import pandas as pd

from quant.utils.dates import ensure_datetime


REQUIRED_MARKET_COLS = [
    "date",
    "ticker",
    "market",
    "open",
    "high",
    "low",
    "close",
    "volume",
]


def clean_market_data(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    missing = [c for c in REQUIRED_MARKET_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Market data missing columns: {missing}")
    df = ensure_datetime(df, "date")
    df = df.drop_duplicates(subset=["date", "ticker", "market"], keep="last")
    for col in ["open", "high", "low", "close", "volume", "turnover", "adj_factor"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    return df
