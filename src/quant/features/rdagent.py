from __future__ import annotations

import pandas as pd


def merge_rdagent_signals(market_df: pd.DataFrame, rdagent_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge RD-Agent signals into features.
    Expected columns: date,ticker,market,rdagent_score
    """
    if rdagent_df is None or rdagent_df.empty:
        return market_df

    df = market_df.merge(rdagent_df, on=["date", "ticker", "market"], how="left")
    if "rdagent_score" in df.columns:
        df["rdagent_score"] = df["rdagent_score"].fillna(0)
    return df
