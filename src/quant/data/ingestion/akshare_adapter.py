from __future__ import annotations

import importlib
from typing import List

import pandas as pd

from quant.data.symbols import a_share_to_akshare


def fetch_daily(universe: List[str], start: str, end: str) -> pd.DataFrame:
    """Fetch A-share daily data via AKShare if installed."""
    if importlib.util.find_spec("akshare") is None:
        raise ImportError("akshare not installed. pip install akshare")
    import akshare as ak  # type: ignore

    frames = []
    for ticker in universe:
        ak_symbol = a_share_to_akshare(ticker)
        df = ak.stock_zh_a_hist(symbol=ak_symbol, start_date=start, end_date=end, adjust="qfq")
        df["ticker"] = ticker
        df["market"] = "A_SHARE"
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out.rename(
        columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "turnover",
        },
        inplace=True,
    )
    return out
