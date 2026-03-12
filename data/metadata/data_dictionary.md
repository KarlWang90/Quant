# Data Dictionary

## Market Data (data/raw/market.csv)
- date: YYYY-MM-DD
- ticker: symbol (e.g., 000001.SZ, 0700.HK)
- market: A_SHARE or HK
- open, high, low, close: float
- volume: number of shares
- turnover: traded value (optional)
- adj_factor: adjustment factor (optional)

## Positions (data/raw/positions.csv)
- date: YYYY-MM-DD
- ticker
- market
- qty
- avg_cost
- currency

## Trades (data/raw/trades.csv)
- date
- ticker
- market
- side: BUY or SELL
- qty
- price
- fee
- currency

## Events/Sentiment (optional)
- date
- ticker
- market
- news_score: numeric sentiment

## RD-Agent Signals (optional)
- date
- ticker
- market
- rdagent_score: numeric score from RD-Agent research
