from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from quant.utils.io import read_csv
from .broker_csv import load_positions_csv, load_trades_csv
from .akshare_adapter import fetch_daily as akshare_fetch_daily
from .baostock_adapter import fetch_daily as baostock_fetch_daily
from .tushare_adapter import fetch_daily as tushare_fetch_daily
from quant.data.universe import load_universe
from quant.data.symbols import a_share_to_baostock


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

def load_rdagent_signals(raw_dir: str | Path) -> pd.DataFrame:
    return _load_optional_csv(Path(raw_dir), "rdagent_signals.csv")


def load_market_data_from_sources(
    raw_dir: str | Path,
    provider_cfg: Optional[Dict[str, str]] = None,
    universe_file: Optional[str | Path] = None,
) -> pd.DataFrame:
    """
    Priority:
    - If provider is csv: use data/raw/market.csv (or sample)
    - Else: use provider (baostock | tushare | akshare)
    """
    raw_dir = Path(raw_dir)
    provider_cfg = provider_cfg or {}
    provider = provider_cfg.get("provider", "csv").lower()

    if provider == "csv":
        market_csv = raw_dir / "market.csv"
        sample_csv = raw_dir / "market.sample.csv"
        if market_csv.exists():
            return load_market_data_csv(market_csv)
        if sample_csv.exists():
            return load_market_data_csv(sample_csv)
        return pd.DataFrame()

    # Provider-based fetch
    if not universe_file:
        universe_file = "config/universe.yaml"

    universe = load_universe(universe_file)
    a_share = universe.get("A_SHARE", [])

    start = provider_cfg.get("start")
    end = provider_cfg.get("end")
    if not start or not end:
        raise ValueError("Provider start/end dates are required for market data fetch.")

    if provider == "baostock":
        symbols = [a_share_to_baostock(x) for x in a_share]
        return baostock_fetch_daily(symbols, start, end)
    if provider == "tushare":
        return tushare_fetch_daily(a_share, start, end)
    if provider == "akshare":
        return akshare_fetch_daily(a_share, start, end)

    raise ValueError(f"Unsupported market data provider: {provider}")
