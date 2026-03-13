# Local Quant Trading System (A-share + HK, Low-Frequency, Low Budget)

This repository implements a local, data-driven quant trading system scaffold with:

- Data ingestion (broker CSV + market data adapters)
- Data cleaning and alignment
- Feature engineering
- Labeling and model training (baseline ML)
- Signal generation
- Portfolio construction with risk constraints
- Human-in-the-loop execution (Open Claw messaging adapter)
- Backtest with delay and cost model

> This is an engineering framework. It is not investment advice.

Chinese user guide:

- `docs/USER_GUIDE_ZH.md`

## Quick Start

1. Create a Python environment and install deps:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy config and env template:

```bash
cp .env.example .env
```

3. Put your broker CSVs in `data/raw/` using the template files:

- `data/raw/positions.sample.csv`
- `data/raw/trades.sample.csv`

4. Put market data in `data/raw/market.sample.csv` format or use an adapter.

5. Run the pipeline:

```bash
python scripts/run_pipeline.py --config config/base.yaml
```

Quick A-share end-to-end smoke test:

```bash
python scripts/demo_a_share_smoke.py
```

6. Inspect outputs:

- `data/processed/`
- `data/features/`
- `data/signals/`
- `data/logs/`

7. Review and confirm pending orders:

```bash
python scripts/approve_orders.py --decision approve
# or
python scripts/approve_orders.py --decision reject
```

8. Backtest historical signal history:

```bash
python scripts/backtest.py --config config/base.yaml
```

## Directory Layout

```
config/                 # YAML configs
src/quant/              # Core code
scripts/                # CLI runners
data/raw/               # Raw inputs (CSV)
data/processed/         # Cleaned data
data/features/          # Feature tables
data/signals/           # Signal outputs
```

## Notes

- The Open Claw adapter defaults to console output. Configure `OPENCLAW_WEBHOOK_URL`
  or `OPENCLAW_MESSAGE_FILE` in `.env` for real messaging.
- A-share / HK calendars are inferred from data date columns by default.
- The baseline model uses sklearn GBDT and can be replaced with deep models later.
- The main pipeline now uses walk-forward scoring, writes `signal_history.csv`,
  and produces `latest_orders.csv` with `approval_status=PENDING`.
- Approval requests are logged under `data/logs/approval_request_*.csv`.

## Real Data Sources (A-share)

The pipeline can fetch A-share data directly using one of these providers:

- `baostock` (free): best for low-budget daily data
- `tushare` (token required): richer data, requires `TUSHARE_TOKEN`
- `akshare` (free): broad coverage but varying stability

Configure in `config/base.yaml`:

```yaml
data_sources:
  market:
    provider: baostock
    start: "2020-01-01"
    end: "2024-12-31"
    universe_file: config/universe.yaml
```

Install the provider you choose:

```bash
pip install baostock
# or
pip install tushare
# or
pip install akshare
```

If using Tushare, set token in `.env`:

```
TUSHARE_TOKEN=your_token_here
```

HK data is not fetched automatically yet. For now, provide HK prices via
`data/raw/market.csv` or extend `hkex_adapter.py` once you have a licensed feed.

## RD-Agent (Separate Research Runner)

RD-Agent is integrated as a **separate** research workflow. You run RD-Agent in a Linux environment,
export its output to CSV, then import into this system as an optional feature.

Steps:

1. Run RD-Agent on Linux and export a CSV of factor scores or signals.
2. Import it into local format:

```bash
python scripts/rdagent/import_signals.py \
  --input /path/to/rdagent_output.csv \
  --date-col date \
  --ticker-col ticker \
  --score-col score \
  --output data/raw/rdagent_signals.csv
```

If `data/raw/rdagent_signals.csv` exists, the pipeline will merge `rdagent_score`
as an extra feature.

## License

Private use only by default. Update as needed.
