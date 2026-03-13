from __future__ import annotations

from pathlib import Path

import pandas as pd

from quant.execution.messenger import Message


def build_trading_suggestion_message(
    orders: pd.DataFrame,
    report_path: str | Path,
    approval_path: str | Path,
    metrics: dict,
    risk_note: str,
    score_col: str = "pred_return",
) -> Message:
    report_path = Path(report_path)
    approval_path = Path(approval_path)

    if orders.empty:
        body = (
            "No executable orders were generated.\n"
            f"Report: {report_path}\n"
            f"Approval file: {approval_path}\n"
            f"Risk note: {risk_note}"
        )
        return Message(title="Trading Suggestions (No Orders)", body=body)

    latest_date = pd.to_datetime(orders["date"]).max().date()
    buy_count = int((orders["side"] == "BUY").sum())
    sell_count = int((orders["side"] == "SELL").sum())

    preview_rows = []
    preview = orders.head(5)
    for _, row in preview.iterrows():
        score_value = row.get(score_col, 0.0)
        preview_rows.append(
            f"{row['side']} {row['ticker']} qty={int(row['trade_qty'])} "
            f"px={row['close']:.2f} score={score_value:.4f}"
        )

    rmse_oos = metrics.get("rmse_oos")
    rmse_text = "n/a" if rmse_oos is None else f"{rmse_oos:.6f}"
    body_lines = [
        f"As of {latest_date}, generated {len(orders)} pending orders.",
        f"Buys: {buy_count}, Sells: {sell_count}, OOS RMSE: {rmse_text}.",
        f"Report: {report_path}",
        f"Approval file: {approval_path}",
        "Preview:",
        *preview_rows,
        f"Risk note: {risk_note}",
    ]
    return Message(
        title=f"Trading Suggestions ({latest_date})",
        body="\n".join(body_lines),
    )
