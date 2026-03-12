#!/usr/bin/env python
import sys
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd

from quant.execution.openclaw import OpenClawMessenger
from quant.execution.messenger import Message


def main() -> None:
    parser = argparse.ArgumentParser(description="Send latest trading suggestions")
    parser.add_argument("--signals", default="data/signals/latest_orders.csv")
    args = parser.parse_args()

    path = Path(args.signals)
    if not path.exists():
        raise FileNotFoundError(f"Signals not found: {path}")
    df = pd.read_csv(path)

    msg = Message(
        title="Trading Suggestions",
        body=f"{len(df)} orders ready for manual approval. File: {path}",
    )
    OpenClawMessenger().send(msg)


if __name__ == "__main__":
    main()
