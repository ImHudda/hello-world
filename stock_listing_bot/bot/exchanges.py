"""Exchange clients that fetch the current set of spot trading pairs."""

from __future__ import annotations

import logging
from dataclasses import dataclass

import requests

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Pair:
    """A spot trading pair on a given exchange."""

    exchange: str
    symbol: str       # exchange-native symbol, e.g. "TSLAX_USDT"
    base: str         # base asset, e.g. "TSLAX"
    quote: str        # quote asset, e.g. "USDT"

    @property
    def key(self) -> str:
        """Stable identity used for de-duplication across polls."""
        return f"{self.exchange}:{self.symbol}"


class GateClient:
    """Gate.io public spot markets."""

    name = "gate"
    URL = "https://api.gateio.ws/api/v4/spot/currency_pairs"

    def __init__(self, timeout: int = 15, session: requests.Session | None = None) -> None:
        self._timeout = timeout
        self._session = session or requests.Session()

    def fetch_pairs(self) -> list[Pair]:
        resp = self._session.get(self.URL, timeout=self._timeout)
        resp.raise_for_status()
        pairs: list[Pair] = []
        for item in resp.json():
            # Skip pairs that are delisted / not yet tradable.
            if item.get("trade_status") not in (None, "tradable"):
                continue
            base = item.get("base")
            quote = item.get("quote")
            symbol = item.get("id") or (f"{base}_{quote}" if base and quote else None)
            if not (base and quote and symbol):
                continue
            pairs.append(Pair(self.name, symbol, base.upper(), quote.upper()))
        return pairs


class BinanceClient:
    """Binance public spot exchange info."""

    name = "binance"
    URL = "https://api.binance.com/api/v3/exchangeInfo"

    def __init__(self, timeout: int = 15, session: requests.Session | None = None) -> None:
        self._timeout = timeout
        self._session = session or requests.Session()

    def fetch_pairs(self) -> list[Pair]:
        resp = self._session.get(self.URL, timeout=self._timeout)
        resp.raise_for_status()
        pairs: list[Pair] = []
        for item in resp.json().get("symbols", []):
            if item.get("status") != "TRADING":
                continue
            base = item.get("baseAsset")
            quote = item.get("quoteAsset")
            symbol = item.get("symbol")
            if not (base and quote and symbol):
                continue
            pairs.append(Pair(self.name, symbol, base.upper(), quote.upper()))
        return pairs
