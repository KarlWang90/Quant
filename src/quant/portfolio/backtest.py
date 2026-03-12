from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class BacktestResult:
    daily: pd.DataFrame
    summary: dict


def run_backtest(
    market_df: pd.DataFrame,
    signals: pd.DataFrame,
    horizon_days: int = 5,
    delay_days: int = 1,
    commission_rate: float = 0.0003,
    stamp_duty_rate: float = 0.001,
    slippage_bps: float = 5.0,
) -> BacktestResult:
    if market_df.empty or signals.empty:
        return BacktestResult(daily=pd.DataFrame(), summary={})

    df = market_df.copy()
    df = df.sort_values(["ticker", "date"]).reset_index(drop=True)

    # Compute forward return for holding period
    df["fwd_ret"] = df.groupby("ticker")["close"].shift(-horizon_days) / df["close"] - 1

    # Apply delay: use price at date+delay for entry
    df["entry_ret"] = df.groupby("ticker")["close"].shift(-delay_days) / df["close"] - 1

    sig = signals.copy()
    sig = sig.merge(df[["date", "ticker", "market", "fwd_ret"]], on=["date", "ticker", "market"], how="left")

    # Apply cost model
    cost = 2 * commission_rate + stamp_duty_rate + (slippage_bps / 10000.0)
    sig["net_ret"] = sig["fwd_ret"] - cost

    daily = sig.groupby("date")["net_ret"].mean().reset_index(name="strategy_ret")
    summary = {
        "mean_ret": float(daily["strategy_ret"].mean()) if not daily.empty else 0.0,
        "vol": float(daily["strategy_ret"].std()) if not daily.empty else 0.0,
        "count_days": int(daily.shape[0]),
    }
    return BacktestResult(daily=daily, summary=summary)
