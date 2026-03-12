from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant.utils.dates import ensure_datetime
from quant.utils.io import read_csv


REQUIRED_POS_COLS = ["date", "ticker", "market", "qty", "avg_cost", "currency"]
REQUIRED_TRD_COLS = ["date", "ticker", "market", "side", "qty", "price", "fee", "currency"]


def _validate_cols(df: pd.DataFrame, required: list[str], name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")


def load_positions_csv(path: str | Path) -> pd.DataFrame:
    df = read_csv(path)
    _validate_cols(df, REQUIRED_POS_COLS, "positions")
    df = ensure_datetime(df, "date")
    return df


def load_trades_csv(path: str | Path) -> pd.DataFrame:
    df = read_csv(path)
    _validate_cols(df, REQUIRED_TRD_COLS, "trades")
    df = ensure_datetime(df, "date")
    return df
