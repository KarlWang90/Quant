from __future__ import annotations

import os
from typing import List

import pandas as pd


def fetch_daily(universe: List[str], start: str, end: str) -> pd.DataFrame:
    try:
        import tushare as ts  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise ImportError("tushare not installed. pip install tushare") from exc

    token = os.getenv("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("Missing TUSHARE_TOKEN in environment")

    ts.set_token(token)
    pro = ts.pro_api()

    frames = []
    for ticker in universe:
        df = pro.daily(ts_code=ticker, start_date=start.replace("-", ""), end_date=end.replace("-", ""))
        if df is None or df.empty:
            continue
        df["ticker"] = ticker
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    out = pd.concat(frames, ignore_index=True)
    out.rename(columns={"trade_date": "date", "open": "open", "high": "high", "low": "low", "close": "close", "vol": "volume"}, inplace=True)
    return out
