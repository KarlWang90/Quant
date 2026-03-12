#!/usr/bin/env python
import sys
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd

from quant.config import load_config
from quant.data.ingestion import load_market_data_from_sources
from quant.data.cleaning import clean_market_data
from quant.portfolio.backtest import run_backtest


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest latest signals")
    parser.add_argument("--config", required=True)
    parser.add_argument("--signals", default="data/signals/latest_orders.csv")
    args = parser.parse_args()

    cfg = load_config(args.config)
    market = clean_market_data(load_market_data_from_sources(cfg.paths["raw_dir"]))
    signals_path = Path(args.signals)
    if not signals_path.exists():
        raise FileNotFoundError(f"Signals not found: {signals_path}")
    signals = pd.read_csv(signals_path)

    result = run_backtest(
        market,
        signals,
        horizon_days=cfg.labels.get("horizon_days", 5),
        delay_days=cfg.trading.get("execution_delay_days", 1),
        commission_rate=cfg.cost_model.get("commission_rate", 0.0003),
        stamp_duty_rate=cfg.cost_model.get("stamp_duty_rate", 0.001),
        slippage_bps=cfg.cost_model.get("slippage_bps", 5),
    )

    print("Backtest Summary:")
    print(result.summary)


if __name__ == "__main__":
    main()
