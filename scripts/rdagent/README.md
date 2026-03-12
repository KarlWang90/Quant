# RD-Agent Integration (Separate Research Runner)

This folder provides a lightweight bridge to integrate RD-Agent outputs into this local quant system.

## How It Works

1. Run RD-Agent **in a Linux environment** to produce a CSV of signals or factor scores.
2. Import the CSV into the local format using the script below.
3. The main pipeline will automatically merge the `rdagent_score` feature if
   `data/raw/rdagent_signals.csv` exists.

## Import Command

```bash
python scripts/rdagent/import_signals.py \
  --input /path/to/rdagent_output.csv \
  --date-col date \
  --ticker-col ticker \
  --market-col market \
  --score-col score \
  --output data/raw/rdagent_signals.csv
```

If your RD-Agent output does not include a market column, omit `--market-col` and use:

```bash
python scripts/rdagent/import_signals.py \
  --input /path/to/rdagent_output.csv \
  --date-col date \
  --ticker-col ticker \
  --score-col score \
  --default-market A_SHARE
```

## Expected Local Format

`data/raw/rdagent_signals.csv`

```
date,ticker,market,rdagent_score
2024-12-02,000001.SZ,A_SHARE,0.15
```
