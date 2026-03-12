from __future__ import annotations

import pandas as pd


def build_price_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    df["ret_1d"] = df.groupby("ticker")["close"].pct_change(1)
    df["ret_5d"] = df.groupby("ticker")["close"].pct_change(5)
    df["vol_5d"] = df.groupby("ticker")["ret_1d"].rolling(5).std().reset_index(level=0, drop=True)
    df["ma_5"] = df.groupby("ticker")["close"].rolling(5).mean().reset_index(level=0, drop=True)
    df["ma_20"] = df.groupby("ticker")["close"].rolling(20).mean().reset_index(level=0, drop=True)
    df["ma_gap"] = df["ma_5"] / df["ma_20"] - 1
    df["vol_chg"] = df.groupby("ticker")["volume"].pct_change(5)
    return df
