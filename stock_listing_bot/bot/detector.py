"""Decide whether a trading pair's base asset is a tokenized stock."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .tickers import KNOWN_TICKERS, STOCK_KEYWORDS

# Quote currencies we ignore when normalising a base asset.
_NON_ALNUM = re.compile(r"[^A-Z0-9]")


def _normalize(base: str) -> str:
    return _NON_ALNUM.sub("", base.upper())


@dataclass(frozen=True)
class StockMatch:
    """Result of classifying a base asset."""

    is_stock: bool
    reason: str = ""
    ticker: str = ""


class StockDetector:
    """Classifies base assets as tokenized stocks via several heuristics."""

    def __init__(self, extra_tickers: list[str] | None = None) -> None:
        extra = {t.upper() for t in (extra_tickers or [])}
        self._tickers = KNOWN_TICKERS | extra

    def classify(self, base_asset: str) -> StockMatch:
        """Return a :class:`StockMatch` for ``base_asset``.

        Heuristics, in order:
          1. Direct match against the known/equity ticker set.
          2. Keyword match (e.g. contains ``STOCK`` / ``XSTOCK``).
          3. Tokenization suffix patterns: ``TSLAX`` or ``TSLA.X`` where the
             stem is a known ticker.
        """
        raw = base_asset.upper()
        base = _normalize(raw)
        if not base:
            return StockMatch(False)

        # 1. Direct ticker match.
        if base in self._tickers:
            return StockMatch(True, "known ticker", base)

        # 2. Keyword match (use the raw form so "X-STOCK" still hits).
        for kw in STOCK_KEYWORDS:
            if kw in raw:
                return StockMatch(True, f"keyword:{kw.lower()}", base)

        # 3. xStocks-style suffix: <TICKER>X / <TICKER>.X / <TICKER>_X.
        if base.endswith("X") and len(base) > 1:
            stem = base[:-1]
            if stem in self._tickers:
                return StockMatch(True, "tokenized suffix", stem)

        return StockMatch(False)
