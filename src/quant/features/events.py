from __future__ import annotations

import pandas as pd


def merge_events(market_df: pd.DataFrame, events_df: pd.DataFrame) -> pd.DataFrame:
    """Merge event/sentiment data; expected columns: date,ticker,market,news_score."""
    if events_df is None or events_df.empty:
        return market_df
    df = market_df.merge(events_df, on=["date", "ticker", "market"], how="left")
    if "news_score" in df.columns:
        df["news_score"] = df["news_score"].fillna(0)
    return df
