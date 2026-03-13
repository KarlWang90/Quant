#!/usr/bin/env python
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import numpy as np
import pandas as pd
import yaml

from quant.cli import run_pipeline
from quant.portfolio.backtest import run_backtest


def build_demo_market_data(dates: pd.DatetimeIndex) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    tickers = {
        "000001.SZ": {"base": 10.0, "drift": 0.06, "volume": 1_800_000},
        "000002.SZ": {"base": 18.0, "drift": 0.03, "volume": 1_500_000},
        "600000.SH": {"base": 9.0, "drift": 0.04, "volume": 2_200_000},
        "510300.SH": {"base": 3.8, "drift": 0.01, "volume": 8_000_000},
    }

    rows: list[dict] = []
    for ticker, meta in tickers.items():
        close = meta["base"]
        for idx, date in enumerate(dates):
            seasonal = np.sin(idx / 9.0) * 0.015
            shock = rng.normal(0, 0.01)
            ret = meta["drift"] / 252.0 + seasonal + shock
            close = max(1.0, close * (1 + ret))
            open_px = close * (1 - rng.normal(0, 0.006))
            high = max(open_px, close) * (1 + abs(rng.normal(0.01, 0.004)))
            low = min(open_px, close) * (1 - abs(rng.normal(0.01, 0.004)))
            volume = int(meta["volume"] * (1 + rng.normal(0, 0.08)))
            turnover = close * volume
            rows.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "ticker": ticker,
                    "market": "A_SHARE",
                    "open": round(open_px, 4),
                    "high": round(high, 4),
                    "low": round(low, 4),
                    "close": round(close, 4),
                    "volume": max(volume, 100_000),
                    "turnover": round(turnover, 2),
                    "adj_factor": 1.0,
                }
            )
    return pd.DataFrame(rows)


def build_demo_fundamentals(dates: pd.DatetimeIndex) -> pd.DataFrame:
    rows: list[dict] = []
    for date in dates[-80:]:
        rows.extend(
            [
                {"date": date.strftime("%Y-%m-%d"), "ticker": "000001.SZ", "market": "A_SHARE", "pe_ttm": 7.8, "pb": 0.85, "roe": 0.12},
                {"date": date.strftime("%Y-%m-%d"), "ticker": "000002.SZ", "market": "A_SHARE", "pe_ttm": 10.5, "pb": 1.35, "roe": 0.10},
                {"date": date.strftime("%Y-%m-%d"), "ticker": "600000.SH", "market": "A_SHARE", "pe_ttm": 6.5, "pb": 0.72, "roe": 0.11},
                {"date": date.strftime("%Y-%m-%d"), "ticker": "510300.SH", "market": "A_SHARE", "pe_ttm": 0.0, "pb": 0.0, "roe": 0.0},
            ]
        )
    return pd.DataFrame(rows)


def build_demo_events(dates: pd.DatetimeIndex) -> pd.DataFrame:
    rows: list[dict] = []
    for idx, date in enumerate(dates[-60:]):
        rows.extend(
            [
                {"date": date.strftime("%Y-%m-%d"), "ticker": "000001.SZ", "market": "A_SHARE", "news_score": 0.15 if idx % 7 in (1, 2) else 0.02},
                {"date": date.strftime("%Y-%m-%d"), "ticker": "000002.SZ", "market": "A_SHARE", "news_score": -0.06 if idx % 11 == 0 else 0.01},
                {"date": date.strftime("%Y-%m-%d"), "ticker": "600000.SH", "market": "A_SHARE", "news_score": 0.08 if idx % 9 == 0 else 0.0},
                {"date": date.strftime("%Y-%m-%d"), "ticker": "510300.SH", "market": "A_SHARE", "news_score": 0.0},
            ]
        )
    return pd.DataFrame(rows)


def build_demo_positions(last_date: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"date": last_date.strftime("%Y-%m-%d"), "ticker": "000002.SZ", "market": "A_SHARE", "qty": 1200, "avg_cost": 18.4, "currency": "CNY"},
            {"date": last_date.strftime("%Y-%m-%d"), "ticker": "600000.SH", "market": "A_SHARE", "qty": 1000, "avg_cost": 9.3, "currency": "CNY"},
        ]
    )


def build_demo_trades(last_date: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"date": (last_date - pd.Timedelta(days=3)).strftime("%Y-%m-%d"), "ticker": "000002.SZ", "market": "A_SHARE", "side": "BUY", "qty": 1200, "price": 18.5, "fee": 5.0, "currency": "CNY"},
            {"date": (last_date - pd.Timedelta(days=6)).strftime("%Y-%m-%d"), "ticker": "600000.SH", "market": "A_SHARE", "side": "BUY", "qty": 1000, "price": 9.2, "fee": 5.0, "currency": "CNY"},
        ]
    )


def build_demo_config(run_dir: Path) -> Path:
    config = {
        "project": {"name": "a-share-smoke", "timezone": "Asia/Shanghai", "currency": "CNY"},
        "paths": {
            "raw_dir": str(run_dir / "raw"),
            "processed_dir": str(run_dir / "processed"),
            "features_dir": str(run_dir / "features"),
            "signals_dir": str(run_dir / "signals"),
            "logs_dir": str(run_dir / "logs"),
        },
        "data_sources": {"market": {"provider": "csv"}},
        "universe": {
            "markets": ["A_SHARE"],
            "instruments": ["STOCK", "ETF"],
            "allow_suspended": False,
            "min_avg_turnover_20d": 1_000_000,
            "max_positions": 3,
        },
        "trading": {
            "lot_size": {"A_SHARE": 100},
            "default_portfolio_value": 100_000,
            "min_cash_buffer": 0.05,
            "rebalance_freq": "WEEKLY",
            "execution_delay_days": 1,
            "max_turnover": 0.4,
        },
        "cost_model": {"commission_rate": 0.0003, "stamp_duty_rate": 0.001, "slippage_bps": 5},
        "labels": {"horizon_days": 5, "target": "forward_return"},
        "model": {"type": "gbdt", "params": {"n_estimators": 50, "max_depth": 2, "learning_rate": 0.05}},
        "validation": {"mode": "walk_forward", "min_train_dates": 40, "retrain_every_n_dates": 10},
        "signal": {"top_k": 3, "min_score": -1.0, "score_name": "pred_return"},
        "messaging": {"channel": "openclaw", "mode": "notify_only", "risk_note": "Demo run: manual approval required"},
        "logging": {"level": "INFO"},
    }
    config_path = run_dir / "config.yaml"
    config_path.write_text(yaml.safe_dump(config, sort_keys=False), encoding="utf-8")
    return config_path


def main() -> None:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = ROOT / "demo_runs" / "a_share_smoke" / timestamp
    for name in ["raw", "processed", "features", "signals", "logs"]:
        (run_dir / name).mkdir(parents=True, exist_ok=True)

    dates = pd.bdate_range("2024-01-02", periods=140)
    last_date = dates[-1]

    build_demo_market_data(dates).to_csv(run_dir / "raw" / "market.csv", index=False)
    build_demo_fundamentals(dates).to_csv(run_dir / "raw" / "fundamentals.csv", index=False)
    build_demo_events(dates).to_csv(run_dir / "raw" / "events.csv", index=False)
    build_demo_positions(last_date).to_csv(run_dir / "raw" / "positions.csv", index=False)
    build_demo_trades(last_date).to_csv(run_dir / "raw" / "trades.csv", index=False)
    config_path = build_demo_config(run_dir)

    run_pipeline(str(config_path))

    latest_orders = pd.read_csv(run_dir / "signals" / "latest_orders.csv")
    signal_history = pd.read_csv(run_dir / "signals" / "signal_history.csv")
    market = pd.read_csv(run_dir / "raw" / "market.csv")
    market["date"] = pd.to_datetime(market["date"])
    signal_history["date"] = pd.to_datetime(signal_history["date"])

    backtest = run_backtest(
        market_df=market,
        signals=signal_history,
        horizon_days=5,
        delay_days=1,
        commission_rate=0.0003,
        stamp_duty_rate=0.001,
        slippage_bps=5,
    )

    print("A-share demo run completed.")
    print(f"Run directory: {run_dir}")
    print(f"Signal history rows: {len(signal_history)}")
    print(f"Latest orders rows: {len(latest_orders)}")
    print(f"Approval requests: {len(list((run_dir / 'logs').glob('approval_request_*.csv')))}")
    print(f"Backtest summary: {backtest.summary}")
    print("Key files:")
    print(f"- config: {config_path}")
    print(f"- latest orders: {run_dir / 'signals' / 'latest_orders.csv'}")
    print(f"- signal history: {run_dir / 'signals' / 'signal_history.csv'}")
    print(f"- approval request: {sorted((run_dir / 'logs').glob('approval_request_*.csv'))[-1]}")


if __name__ == "__main__":
    main()
