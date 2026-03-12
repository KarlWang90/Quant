from __future__ import annotations

import argparse
from pathlib import Path

from quant.config import load_config
from quant.utils.logging import setup_logging
from quant.utils.io import write_csv
from quant.data.ingestion import (
    load_market_data_from_sources,
    load_fundamentals,
    load_events,
)
from quant.data.cleaning import clean_market_data
from quant.data.corporate_actions import apply_adjustments
from quant.features.price_volume import build_price_volume_features
from quant.features.fundamentals import merge_fundamentals
from quant.features.events import merge_events
from quant.features.cross_market import add_market_context
from quant.labels.future_return import add_forward_return
from quant.models.train import train_model
from quant.models.baseline_gbdt import predict_gbdt
from quant.signals.signal_engine import build_signals
from quant.portfolio.constraints import apply_constraints
from quant.portfolio.optimizer import equal_weight
from quant.execution.order_builder import build_orders
from quant.execution.openclaw import OpenClawMessenger
from quant.execution.messenger import Message
from quant.monitoring.report import generate_signal_report


def run_pipeline(config_path: str) -> None:
    cfg = load_config(config_path)
    setup_logging(cfg.paths.get("logs_dir", "data/logs"), cfg.data.get("logging", {}).get("level", "INFO"))

    market = load_market_data_from_sources(cfg.paths["raw_dir"])
    market = clean_market_data(market)
    market = apply_adjustments(market)

    if market.empty:
        raise ValueError("No market data found. Provide data/raw/market.csv or enable an adapter.")

    processed_path = Path(cfg.paths.get("processed_dir", "data/processed")) / "market.csv"
    write_csv(market, processed_path)

    fundamentals = load_fundamentals(cfg.paths["raw_dir"])
    events = load_events(cfg.paths["raw_dir"])

    features = build_price_volume_features(market)
    features = merge_fundamentals(features, fundamentals)
    features = merge_events(features, events)
    features = add_market_context(features)
    features = add_forward_return(features, horizon=cfg.labels.get("horizon_days", 5))

    features_path = Path(cfg.paths.get("features_dir", "data/features")) / "features.csv"
    write_csv(features, features_path)

    model_result = train_model(features, cfg.model, cfg.labels.get("target", "forward_return"))
    scored = predict_gbdt(model_result.model, features)

    signals = build_signals(
        scored,
        score_col=cfg.signal.get("score_name", "pred_return"),
        top_k=cfg.signal.get("top_k", 10),
        min_score=cfg.signal.get("min_score", 0.0),
    )
    signals = apply_constraints(signals, max_positions=cfg.universe.get("max_positions", 15))
    signals = equal_weight(signals)

    orders = build_orders(signals)
    report_path = generate_signal_report(orders, cfg.paths.get("signals_dir", "data/signals"))

    msg = Message(
        title=f"Trading Suggestions ({report_path.name})",
        body=f"Generated {len(orders)} orders. Report saved to {report_path}.",
    )
    OpenClawMessenger().send(msg)

    write_csv(orders, Path(cfg.paths.get("signals_dir", "data/signals")) / "latest_orders.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Quant Trading System")
    parser.add_argument("--config", required=True, help="Path to config yaml")
    args = parser.parse_args()
    run_pipeline(args.config)


if __name__ == "__main__":
    main()
