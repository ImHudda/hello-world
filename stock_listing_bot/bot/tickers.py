"""Reference set of equity tickers used to recognise tokenized stocks.

This is intentionally a curated, well-known subset (large caps + the names
most commonly issued as on-chain "xStocks"). It does not need to be
exhaustive: the detector also recognises the generic ``<TICKER>X`` /
``<TICKER>.X`` tokenization patterns and an explicit ``EXTRA_TICKERS`` list.
"""

from __future__ import annotations

# Common US equities frequently issued as tokenized stocks.
KNOWN_TICKERS: frozenset[str] = frozenset(
    {
        "AAPL", "ABNB", "AMD", "AMZN", "AVGO", "BABA", "BAC", "BRK", "C",
        "CMCSA", "COIN", "CRCL", "CRM", "CRWD", "CSCO", "CVX", "DELL", "DIS",
        "GLD", "GME", "GOOG", "GOOGL", "GS", "HOOD", "IBM", "INTC", "JNJ",
        "JPM", "KO", "LLY", "MA", "MCD", "META", "MRVL", "MSFT", "MSTR",
        "NFLX", "NKE", "NVDA", "ORCL", "PEP", "PFE", "PG", "PLTR", "PYPL",
        "QCOM", "QQQ", "SBUX", "SHOP", "SMCI", "SNAP", "SPY", "SQ", "T",
        "TGT", "TSLA", "TSM", "UBER", "UNH", "V", "WMT", "XOM",
        # Pre-IPO / private names that have appeared as tokenized assets.
        "SPACEX", "OPENAI", "STRIPE", "ANTHROPIC", "DATABRICKS", "BYTEDANCE",
    }
)

# Keywords that strongly imply a tokenized-stock / equity product.
STOCK_KEYWORDS: tuple[str, ...] = (
    "STOCK",
    "XSTOCK",
    "TOKENIZED",
    "EQUITY",
    "PREIPO",
    "PRE-IPO",
)
