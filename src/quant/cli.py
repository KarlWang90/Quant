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
    load_positions_snapshot,
    load_rdagent_signals,
    load_trade_history,
)
from quant.data.cleaning import clean_market_data
from quant.data.corporate_actions import apply_adjustments
from quant.features.price_volume import build_price_volume_features
from quant.features.fundamentals import merge_fundamentals
from quant.features.events import merge_events
from quant.features.rdagent import merge_rdagent_signals
from quant.features.cross_market import add_market_context
from quant.labels.future_return import add_forward_return
from quant.models.train import walk_forward_train_and_predict
from quant.signals.signal_engine import build_signals
from quant.portfolio.constraints import apply_constraints
from quant.portfolio.optimizer import equal_weight
from quant.execution.approval import write_approval_request
from quant.execution.message_builder import build_trading_suggestion_message
from quant.execution.order_builder import build_orders
from quant.execution.openclaw import OpenClawMessenger
from quant.monitoring.report import generate_signal_report


def run_pipeline(config_path: str) -> None:
    cfg = load_config(config_path)
    setup_logging(cfg.paths.get("logs_dir", "data/logs"), cfg.data.get("logging", {}).get("level", "INFO"))

    market_provider = cfg.data_sources.get("market", {})
    market = load_market_data_from_sources(
        cfg.paths["raw_dir"],
        provider_cfg=market_provider,
        universe_file=market_provider.get("universe_file"),
    )
    market = clean_market_data(market)
    market = apply_adjustments(market)

    if market.empty:
        raise ValueError("No market data found. Provide data/raw/market.csv or enable an adapter.")

    processed_path = Path(cfg.paths.get("processed_dir", "data/processed")) / "market.csv"
    write_csv(market, processed_path)

    fundamentals = load_fundamentals(cfg.paths["raw_dir"])
    events = load_events(cfg.paths["raw_dir"])
    rdagent_signals = load_rdagent_signals(cfg.paths["raw_dir"])
    positions = load_positions_snapshot(cfg.paths["raw_dir"])
    trades = load_trade_history(cfg.paths["raw_dir"])

    features = build_price_volume_features(market)
    features = merge_fundamentals(features, fundamentals)
    features = merge_events(features, events)
    features = merge_rdagent_signals(features, rdagent_signals)
    features = add_market_context(features)
    features = add_forward_return(features, horizon=cfg.labels.get("horizon_days", 5))

    features_path = Path(cfg.paths.get("features_dir", "data/features")) / "features.csv"
    write_csv(features, features_path)

    model_result = walk_forward_train_and_predict(
        features,
        cfg.model,
        cfg.labels.get("target", "forward_return"),
        min_train_dates=cfg.validation.get("min_train_dates", 60),
        retrain_every_n_dates=cfg.validation.get("retrain_every_n_dates", 20),
    )
    scored = model_result.model

    signals = build_signals(
        scored,
        score_col=cfg.signal.get("score_name", "pred_return"),
        top_k=cfg.signal.get("top_k", 10),
        min_score=cfg.signal.get("min_score", 0.0),
    )
    signals = apply_constraints(
        signals,
        context_df=scored,
        max_positions=cfg.universe.get("max_positions", 15),
        min_avg_turnover_20d=cfg.universe.get("min_avg_turnover_20d", 0.0),
        allow_suspended=cfg.universe.get("allow_suspended", False),
    )
    signals = equal_weight(signals)
    write_csv(signals, Path(cfg.paths.get("signals_dir", "data/signals")) / "signal_history.csv")

    orders = build_orders(
        signals,
        market,
        positions=positions,
        trades=trades,
        trading_cfg=cfg.trading,
        cost_cfg=cfg.cost_model,
        score_col=cfg.signal.get("score_name", "pred_return"),
    )
    report_path = generate_signal_report(orders, cfg.paths.get("signals_dir", "data/signals"))
    latest_orders_path = Path(cfg.paths.get("signals_dir", "data/signals")) / "latest_orders.csv"
    write_csv(orders, latest_orders_path)
    approval_path = write_approval_request(orders, cfg.paths.get("logs_dir", "data/logs"))

    msg = build_trading_suggestion_message(
        orders,
        report_path=report_path,
        approval_path=approval_path,
        metrics=model_result.metrics,
        risk_note=cfg.messaging.get("risk_note", "Manual approval required."),
        score_col=cfg.signal.get("score_name", "pred_return"),
    )
    OpenClawMessenger().send(msg)


def main() -> None:
    parser = argparse.ArgumentParser(description="Local Quant Trading System")
    parser.add_argument("--config", required=True, help="Path to config yaml")
    args = parser.parse_args()
    run_pipeline(args.config)


if __name__ == "__main__":
    main()
