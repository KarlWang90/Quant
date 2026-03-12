from __future__ import annotations

from pathlib import Path
from typing import Dict

import pandas as pd

from quant.utils.io import read_csv
from .broker_csv import load_positions_csv, load_trades_csv


def load_market_data_csv(path: str | Path) -> pd.DataFrame:
    df = read_csv(path)
    return df


def load_positions(path: str | Path) -> pd.DataFrame:
    return load_positions_csv(path)


def load_trades(path: str | Path) -> pd.DataFrame:
    return load_trades_csv(path)


def _load_optional_csv(raw_dir: Path, name: str) -> pd.DataFrame:
    path = raw_dir / name
    if path.exists():
        return read_csv(path)
    return pd.DataFrame()


def load_fundamentals(raw_dir: str | Path) -> pd.DataFrame:
    return _load_optional_csv(Path(raw_dir), "fundamentals.csv")


def load_events(raw_dir: str | Path) -> pd.DataFrame:
    return _load_optional_csv(Path(raw_dir), "events.csv")


def load_market_data_from_sources(
    raw_dir: str | Path,
    universe: Dict[str, list[str]] | None = None,
) -> pd.DataFrame:
    """
    Priority: raw market CSV if exists, else empty dataframe.
    Adapters can be plugged in later (AKShare/Baostock/Tushare/HKEX).
    """
    raw_dir = Path(raw_dir)
    market_csv = raw_dir / "market.csv"
    sample_csv = raw_dir / "market.sample.csv"
    if market_csv.exists():
        return load_market_data_csv(market_csv)
    if sample_csv.exists():
        return load_market_data_csv(sample_csv)
    return pd.DataFrame()
