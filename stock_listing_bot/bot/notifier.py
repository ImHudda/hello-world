"""Notification sinks: console logging and Telegram."""

from __future__ import annotations

import logging

import requests

log = logging.getLogger(__name__)


class ConsoleNotifier:
    """Logs alerts to stdout via the logging module."""

    def send(self, message: str) -> bool:
        log.info("ALERT\n%s", message)
        return True


class TelegramNotifier:
    """Sends alerts to a Telegram chat through the Bot API."""

    def __init__(self, bot_token: str, chat_id: str, timeout: int = 15) -> None:
        self._url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        self._chat_id = chat_id
        self._timeout = timeout
        self._session = requests.Session()

    def send(self, message: str) -> bool:
        try:
            resp = self._session.post(
                self._url,
                json={
                    "chat_id": self._chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": True,
                },
                timeout=self._timeout,
            )
            resp.raise_for_status()
            return True
        except requests.RequestException as exc:
            log.error("Telegram send failed: %s", exc)
            return False


class MultiNotifier:
    """Fans a message out to several notifiers; succeeds if any one does."""

    def __init__(self, *notifiers) -> None:
        self._notifiers = [n for n in notifiers if n is not None]

    def send(self, message: str) -> bool:
        results = [n.send(message) for n in self._notifiers]
        return any(results)
