"""Runtime configuration, loaded from environment variables.

All settings have sensible defaults so the bot can run in a dry mode
(console only) without any setup. Telegram alerts activate automatically
once ``TELEGRAM_BOT_TOKEN`` and ``TELEGRAM_CHAT_ID`` are provided.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _env_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_list(name: str) -> list[str]:
    raw = os.getenv(name, "")
    return [item.strip().upper() for item in raw.split(",") if item.strip()]


@dataclass
class Config:
    """Bot configuration resolved from the environment."""

    # Telegram credentials. When both are set, alerts are sent.
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    # Seconds between polling cycles.
    poll_interval: int = field(default_factory=lambda: _env_int("POLL_INTERVAL", 120))

    # HTTP request timeout in seconds.
    request_timeout: int = field(default_factory=lambda: _env_int("REQUEST_TIMEOUT", 15))

    # Which exchanges to poll.
    enable_gate: bool = field(default_factory=lambda: _env_bool("ENABLE_GATE", True))
    enable_binance: bool = field(default_factory=lambda: _env_bool("ENABLE_BINANCE", True))

    # Alert on every match found on the very first cycle. Off by default so a
    # fresh start just records a baseline instead of spamming every existing pair.
    alert_on_first_run: bool = field(default_factory=lambda: _env_bool("ALERT_ON_FIRST_RUN", False))

    # Extra equity tickers to treat as stock tokens (comma separated).
    extra_tickers: list[str] = field(default_factory=lambda: _env_list("EXTRA_TICKERS"))

    # Where the seen-symbols state is persisted.
    state_file: str = field(default_factory=lambda: os.getenv("STATE_FILE", "seen_symbols.json"))

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.telegram_bot_token and self.telegram_chat_id)
