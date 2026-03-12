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

6. Inspect outputs:

- `data/processed/`
- `data/features/`
- `data/signals/`
- `data/logs/`

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

## License

Private use only by default. Update as needed.
