from __future__ import annotations

import math
from typing import Any

import pandas as pd


def _latest_positions_snapshot(positions: pd.DataFrame, as_of_date: pd.Timestamp) -> pd.DataFrame:
    if positions is None or positions.empty:
        return pd.DataFrame(columns=["ticker", "market", "qty", "avg_cost", "currency"])
    eligible = positions[positions["date"] <= as_of_date].copy()
    if eligible.empty:
        return pd.DataFrame(columns=["ticker", "market", "qty", "avg_cost", "currency"])
    latest_date = eligible["date"].max()
    return eligible[eligible["date"] == latest_date].copy()


def _latest_market_snapshot(market_df: pd.DataFrame, as_of_date: pd.Timestamp) -> pd.DataFrame:
    eligible = market_df[market_df["date"] <= as_of_date].copy()
    if eligible.empty:
        return pd.DataFrame(columns=["ticker", "market", "market_date", "close"])
    eligible = eligible.sort_values(["ticker", "market", "date"])
    latest = eligible.groupby(["ticker", "market"], as_index=False).tail(1).copy()
    latest.rename(columns={"date": "market_date"}, inplace=True)
    return latest


def _latest_trade_context(trades: pd.DataFrame, as_of_date: pd.Timestamp) -> pd.DataFrame:
    if trades is None or trades.empty:
        return pd.DataFrame(columns=["ticker", "market", "last_trade_date", "last_trade_side"])
    eligible = trades[trades["date"] <= as_of_date].copy()
    if eligible.empty:
        return pd.DataFrame(columns=["ticker", "market", "last_trade_date", "last_trade_side"])
    eligible = eligible.sort_values(["ticker", "market", "date"])
    latest = eligible.groupby(["ticker", "market"], as_index=False).tail(1).copy()
    latest.rename(columns={"date": "last_trade_date", "side": "last_trade_side"}, inplace=True)
    return latest[["ticker", "market", "last_trade_date", "last_trade_side"]]


def _round_to_lot(raw_qty: float, lot_size: int) -> int:
    if pd.isna(raw_qty) or raw_qty == 0:
        return 0
    lot = max(int(lot_size), 1)
    scaled = math.floor(abs(raw_qty) / lot) * lot
    return int(math.copysign(scaled, raw_qty))


def _estimate_cost(trade_value: float, side: str, market: str, cost_cfg: dict[str, Any]) -> float:
    commission = float(cost_cfg.get("commission_rate", 0.0))
    stamp = float(cost_cfg.get("stamp_duty_rate", 0.0))
    slippage = float(cost_cfg.get("slippage_bps", 0.0)) / 10000.0
    total = trade_value * commission
    if side == "SELL" and market == "A_SHARE":
        total += trade_value * stamp
    total += trade_value * slippage
    return total


def _build_reason(row: pd.Series) -> str:
    if row["side"] == "SELL" and row["target_weight"] == 0:
        return "Exit position because it is no longer in the target basket"
    if row["side"] == "SELL":
        return "Trim position toward target weight"
    if row["current_qty"] == 0:
        return "Enter new top-ranked signal"
    return "Increase position toward target weight"


def build_orders(
    signals: pd.DataFrame,
    market_df: pd.DataFrame,
    positions: pd.DataFrame | None = None,
    trades: pd.DataFrame | None = None,
    trading_cfg: dict[str, Any] | None = None,
    cost_cfg: dict[str, Any] | None = None,
    score_col: str = "pred_return",
) -> pd.DataFrame:
    if signals.empty or market_df.empty:
        return pd.DataFrame()

    trading_cfg = trading_cfg or {}
    cost_cfg = cost_cfg or {}

    signal_date = pd.to_datetime(signals["date"]).max()
    latest_signals = signals[signals["date"] == signal_date].copy()
    if latest_signals.empty:
        return pd.DataFrame()

    market_snapshot = _latest_market_snapshot(market_df, signal_date)
    latest_positions = _latest_positions_snapshot(positions, signal_date)
    latest_trades = _latest_trade_context(trades, signal_date)

    latest_signals = latest_signals.copy()
    latest_signals["target_weight"] = latest_signals["weight"].fillna(0.0)
    latest_signals.rename(columns={"date": "signal_date"}, inplace=True)
    latest_signals = latest_signals[
        ["signal_date", "ticker", "market", score_col, "target_weight", "avg_turnover_20d"]
        if "avg_turnover_20d" in latest_signals.columns
        else ["signal_date", "ticker", "market", score_col, "target_weight"]
    ]

    current = latest_positions.rename(columns={"qty": "current_qty", "date": "position_date"})
    combined = current.merge(
        latest_signals,
        on=["ticker", "market"],
        how="outer",
    )
    if "signal_date" not in combined.columns:
        combined["signal_date"] = pd.NaT
    if "position_date" not in combined.columns:
        combined["position_date"] = pd.NaT
    combined["date"] = combined["signal_date"].fillna(combined["position_date"]).fillna(signal_date)
    combined["current_qty"] = combined["current_qty"].fillna(0.0)
    if "avg_cost" not in combined.columns:
        combined["avg_cost"] = 0.0
    else:
        combined["avg_cost"] = combined["avg_cost"].fillna(0.0)
    combined["target_weight"] = combined["target_weight"].fillna(0.0)
    if score_col not in combined.columns:
        combined[score_col] = 0.0
    else:
        combined[score_col] = combined[score_col].fillna(0.0)

    combined = combined.merge(
        market_snapshot[["ticker", "market", "market_date", "close"]],
        on=["ticker", "market"],
        how="left",
    )
    combined = combined.merge(
        latest_trades,
        on=["ticker", "market"],
        how="left",
    )
    combined = combined.dropna(subset=["close"])
    if combined.empty:
        return pd.DataFrame()

    combined["current_value"] = combined["current_qty"] * combined["close"]
    default_portfolio_value = float(trading_cfg.get("default_portfolio_value", 100000.0))
    portfolio_value = max(float(combined["current_value"].sum()), default_portfolio_value)
    min_cash_buffer = float(trading_cfg.get("min_cash_buffer", 0.0))
    investable_value = portfolio_value * max(0.0, 1.0 - min_cash_buffer)

    combined["target_value"] = investable_value * combined["target_weight"]
    combined["delta_value"] = combined["target_value"] - combined["current_value"]

    max_turnover = float(trading_cfg.get("max_turnover", 1.0))
    allowed_turnover_value = portfolio_value * max_turnover
    raw_turnover_value = float(combined["delta_value"].abs().sum())
    if raw_turnover_value > 0 and raw_turnover_value > allowed_turnover_value > 0:
        scale = allowed_turnover_value / raw_turnover_value
        combined["delta_value"] = combined["delta_value"] * scale

    lot_sizes = trading_cfg.get("lot_size", {})
    combined["lot_size"] = combined["market"].map(lot_sizes).fillna(1).astype(int)
    combined["raw_order_qty"] = combined["delta_value"] / combined["close"]
    combined["order_qty"] = combined.apply(
        lambda row: _round_to_lot(row["raw_order_qty"], int(row["lot_size"])),
        axis=1,
    )
    combined = combined[combined["order_qty"] != 0].copy()
    if combined.empty:
        return combined

    combined["side"] = combined["order_qty"].apply(lambda qty: "BUY" if qty > 0 else "SELL")
    combined["trade_qty"] = combined["order_qty"].abs()
    combined["target_qty"] = combined["current_qty"] + combined["order_qty"]
    combined["estimated_trade_value"] = combined["trade_qty"] * combined["close"]
    combined["estimated_cost"] = combined.apply(
        lambda row: _estimate_cost(
            float(row["estimated_trade_value"]),
            str(row["side"]),
            str(row["market"]),
            cost_cfg,
        ),
        axis=1,
    )
    combined["days_since_last_trade"] = (
        (signal_date - pd.to_datetime(combined["last_trade_date"])).dt.days
        if "last_trade_date" in combined.columns
        else pd.NA
    )
    combined["order_type"] = combined["side"]
    combined["reason"] = combined.apply(_build_reason, axis=1)
    combined["approval_status"] = "PENDING"

    ordered_cols = [
        "date",
        "ticker",
        "market",
        "side",
        "trade_qty",
        "close",
        "current_qty",
        "target_qty",
        "target_weight",
        score_col,
        "estimated_trade_value",
        "estimated_cost",
        "reason",
        "approval_status",
        "market_date",
        "last_trade_date",
        "days_since_last_trade",
    ]
    if "avg_turnover_20d" in combined.columns:
        ordered_cols.insert(10, "avg_turnover_20d")
    return combined[ordered_cols].sort_values(["side", score_col], ascending=[True, False]).reset_index(drop=True)
