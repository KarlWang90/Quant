from __future__ import annotations

import pandas as pd


def merge_fundamentals(market_df: pd.DataFrame, fundamental_df: pd.DataFrame) -> pd.DataFrame:
    """Left join fundamentals by date/ticker/market if provided."""
    if fundamental_df is None or fundamental_df.empty:
        return market_df
    df = market_df.merge(fundamental_df, on=["date", "ticker", "market"], how="left")
    return df
