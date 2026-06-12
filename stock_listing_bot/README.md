# Stock-token Listing Bot

Watches **Gate.io** and **Binance** spot markets and alerts you on **Telegram**
the moment a new **tokenized-stock** trading pair is listed (e.g. `TSLAX`,
`NVDAX`, `SPACEX`, or anything matching a known equity ticker / `xStock`
pattern).

It polls each exchange's public REST API on an interval, compares against a
persisted snapshot of pairs it has already seen, and fires an alert only for
*newly* listed pairs whose base asset is classified as a stock token.

## How it works

```
Gate.io API ─┐
             ├─▶ collect pairs ─▶ filter (new & not seen) ─▶ StockDetector ─▶ Telegram + console
Binance API ─┘                                    │
                                          seen_symbols.json (state)
```

**Detection** (`bot/detector.py`) flags a base asset as a stock token when:
1. it matches a known equity ticker (`AAPL`, `TSLA`, `SPACEX`, …), or
2. it contains a stock keyword (`STOCK`, `XSTOCK`, `TOKENIZED`, …), or
3. it uses the tokenization suffix pattern `<TICKER>X` / `<TICKER>.X`
   (e.g. `TSLAX` → `TSLA`).

Extend coverage at runtime with `EXTRA_TICKERS=RBLX,RIVN`.

## Setup

```bash
cd stock_listing_bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your Telegram credentials
```

### Telegram credentials
1. Create a bot with [@BotFather](https://t.me/BotFather) → get the **bot token**.
2. Message your new bot, then visit
   `https://api.telegram.org/bot<TOKEN>/getUpdates` to find your **chat id**.
3. Put both in `.env` (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).

Without Telegram credentials the bot still runs and prints alerts to the console.

## Usage

Load the env file and run:

```bash
set -a; source .env; set +a

# Single cycle (records baseline on first run, then exits):
python -m bot --once

# Continuous watcher:
python -m bot
```

> The first run records a baseline of existing pairs **without** alerting
> (so you aren't spammed by every pair already listed). Set
> `ALERT_ON_FIRST_RUN=true` to alert on existing matches too.

## Configuration

All settings come from environment variables — see [`.env.example`](.env.example).

| Variable | Default | Description |
|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | — | Telegram bot token (enables Telegram alerts) |
| `TELEGRAM_CHAT_ID` | — | Telegram chat id to send alerts to |
| `POLL_INTERVAL` | `120` | Seconds between poll cycles |
| `REQUEST_TIMEOUT` | `15` | HTTP timeout per request (s) |
| `ENABLE_GATE` | `true` | Poll Gate.io |
| `ENABLE_BINANCE` | `true` | Poll Binance |
| `ALERT_ON_FIRST_RUN` | `false` | Alert on matches during the first cycle |
| `EXTRA_TICKERS` | — | Extra tickers to treat as stocks (CSV) |
| `STATE_FILE` | `seen_symbols.json` | Where seen pairs are persisted |

## Tests

```bash
pip install pytest
python -m pytest -q
```

## Notes / disclaimer
- Uses only public, unauthenticated market-data endpoints; no API keys needed.
- Listing detection is best-effort and not financial advice. Tokenized equities
  are restricted in some jurisdictions — verify availability and legality before
  trading.
