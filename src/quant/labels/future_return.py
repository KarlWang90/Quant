from __future__ import annotations

import pandas as pd


def add_forward_return(df: pd.DataFrame, horizon: int = 5) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)
    df["forward_return"] = (
        df.groupby("ticker")["close"].shift(-horizon) / df["close"] - 1
    )
    return df
