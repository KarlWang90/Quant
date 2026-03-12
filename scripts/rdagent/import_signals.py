#!/usr/bin/env python
import sys
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

import pandas as pd


def main() -> None:
    parser = argparse.ArgumentParser(description="Import RD-Agent signals into local format")
    parser.add_argument("--input", required=True, help="Path to RD-Agent CSV output")
    parser.add_argument("--date-col", default="date")
    parser.add_argument("--ticker-col", default="ticker")
    parser.add_argument("--market-col", default="market")
    parser.add_argument("--score-col", default="score")
    parser.add_argument("--default-market", default="A_SHARE")
    parser.add_argument("--output", default="data/raw/rdagent_signals.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.market_col not in df.columns:
        df[args.market_col] = args.default_market

    out = pd.DataFrame(
        {
            "date": df[args.date_col],
            "ticker": df[args.ticker_col],
            "market": df[args.market_col],
            "rdagent_score": df[args.score_col],
        }
    )
    out.to_csv(args.output, index=False)
    print(f"Saved {len(out)} rows to {args.output}")


if __name__ == "__main__":
    main()
