from __future__ import annotations

import pandas as pd


def add_market_context(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "ret_1d" not in out.columns:
        out["ret_1d"] = out.groupby("ticker")["close"].pct_change(1)

    market_ret = (
        out.groupby(["market", "date"])  
        ["ret_1d"].mean()
        .reset_index(name="market_ret_1d")
    )
    out = out.merge(market_ret, on=["market", "date"], how="left")
    return out
