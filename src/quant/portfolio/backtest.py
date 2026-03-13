from __future__ import annotations

from dataclasses import dataclass

import numpy as np
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

    df["entry_close"] = df.groupby("ticker")["close"].shift(-delay_days)
    df["exit_close"] = df.groupby("ticker")["close"].shift(-(delay_days + horizon_days))
    df["fwd_ret"] = df["exit_close"] / df["entry_close"] - 1

    sig = signals.copy()
    sig = sig.merge(
        df[["date", "ticker", "market", "entry_close", "exit_close", "fwd_ret"]],
        on=["date", "ticker", "market"],
        how="left",
    )
    sig = sig.dropna(subset=["fwd_ret"])

    # Apply cost model
    cost = 2 * commission_rate + stamp_duty_rate + (slippage_bps / 10000.0)
    sig["net_ret"] = sig["fwd_ret"] - cost

    if "weight" in sig.columns:
        daily = (
            sig.groupby("date")
            .apply(
                lambda rows: np.average(
                    rows["net_ret"],
                    weights=rows["weight"].abs().clip(lower=1e-9),
                )
            )
            .reset_index(name="strategy_ret")
        )
    else:
        daily = sig.groupby("date")["net_ret"].mean().reset_index(name="strategy_ret")
    summary = {
        "mean_ret": float(daily["strategy_ret"].mean()) if not daily.empty else 0.0,
        "vol": float(daily["strategy_ret"].std()) if not daily.empty else 0.0,
        "count_days": int(daily.shape[0]),
        "delay_days": int(delay_days),
        "horizon_days": int(horizon_days),
    }
    return BacktestResult(daily=daily, summary=summary)
