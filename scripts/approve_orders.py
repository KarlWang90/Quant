#!/usr/bin/env python
import sys
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd

from quant.execution.approval import record_approval


def main() -> None:
    parser = argparse.ArgumentParser(description="Approve or reject pending orders")
    parser.add_argument("--orders", default="data/signals/latest_orders.csv")
    parser.add_argument("--decision", choices=["approve", "reject"], required=True)
    parser.add_argument("--log-dir", default="data/logs")
    args = parser.parse_args()

    orders_path = Path(args.orders)
    if not orders_path.exists():
        raise FileNotFoundError(f"Orders not found: {orders_path}")

    orders = pd.read_csv(orders_path)
    output_path = record_approval(orders, args.decision, args.log_dir)
    print(f"Saved approval decision to {output_path}")


if __name__ == "__main__":
    main()
