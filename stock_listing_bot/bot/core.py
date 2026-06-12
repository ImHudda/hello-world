"""Core polling loop tying exchanges, detection, state and alerts together."""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone

import requests

from .config import Config
from .detector import StockDetector
from .exchanges import BinanceClient, GateClient, Pair
from .notifier import ConsoleNotifier, MultiNotifier, TelegramNotifier
from .state import SeenStore

log = logging.getLogger(__name__)


def build_notifier(config: Config):
    console = ConsoleNotifier()
    telegram = None
    if config.telegram_enabled:
        telegram = TelegramNotifier(
            config.telegram_bot_token,
            config.telegram_chat_id,
            timeout=config.request_timeout,
        )
        log.info("Telegram alerts enabled.")
    else:
        log.info("Telegram not configured — console alerts only.")
    return MultiNotifier(console, telegram)


def format_alert(pair: Pair, reason: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return (
        "🚨 <b>New tokenized-stock listing</b>\n"
        f"<b>Exchange:</b> {pair.exchange.capitalize()}\n"
        f"<b>Pair:</b> {pair.symbol}\n"
        f"<b>Base:</b> {pair.base}  <b>Quote:</b> {pair.quote}\n"
        f"<b>Matched:</b> {reason}\n"
        f"<b>Seen:</b> {ts}"
    )


class ListingBot:
    """Polls configured exchanges and alerts on new tokenized-stock pairs."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.detector = StockDetector(extra_tickers=config.extra_tickers)
        self.store = SeenStore(config.state_file)
        self.notifier = build_notifier(config)

        session = requests.Session()
        self.clients = []
        if config.enable_gate:
            self.clients.append(GateClient(config.request_timeout, session))
        if config.enable_binance:
            self.clients.append(BinanceClient(config.request_timeout, session))
        if not self.clients:
            raise ValueError("No exchanges enabled (set ENABLE_GATE / ENABLE_BINANCE).")

    def _collect_pairs(self) -> list[Pair]:
        pairs: list[Pair] = []
        for client in self.clients:
            try:
                fetched = client.fetch_pairs()
                log.debug("%s returned %d pairs", client.name, len(fetched))
                pairs.extend(fetched)
            except requests.RequestException as exc:
                log.warning("Fetch from %s failed: %s", client.name, exc)
        return pairs

    def run_once(self) -> list[Pair]:
        """Run a single poll cycle. Returns the stock pairs that were alerted."""
        if not self.store._loaded:  # lazy first load
            self.store.load()

        first_run = self.store.is_empty
        suppress = first_run and not self.config.alert_on_first_run

        pairs = self._collect_pairs()
        alerted: list[Pair] = []

        for pair in pairs:
            if pair.key in self.store:
                continue
            match = self.detector.classify(pair.base)
            if match.is_stock:
                if suppress:
                    log.info(
                        "Baseline (suppressed) stock pair: %s (%s)",
                        pair.key, match.reason,
                    )
                else:
                    if self.notifier.send(format_alert(pair, match.reason)):
                        alerted.append(pair)
            self.store.add(pair.key)

        # Only persist once we have a full snapshot (avoid baselining a partial
        # fetch as "seen" if every exchange failed).
        if pairs:
            self.store.save()
        if first_run:
            log.info(
                "Baseline recorded (%d pairs). Future new stock listings will alert.",
                len(pairs),
            )
        return alerted

    def run_forever(self) -> None:
        log.info(
            "Starting listing bot. Exchanges=%s interval=%ss",
            [c.name for c in self.clients], self.config.poll_interval,
        )
        while True:
            try:
                self.run_once()
            except Exception:  # noqa: BLE001 - keep the loop alive
                log.exception("Unexpected error during poll cycle")
            time.sleep(self.config.poll_interval)
