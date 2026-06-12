"""Tests for the polling/alerting core using a fake exchange + notifier."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.config import Config  # noqa: E402
from bot.core import ListingBot  # noqa: E402
from bot.exchanges import Pair  # noqa: E402


class FakeClient:
    name = "fake"

    def __init__(self, pairs):
        self._pairs = pairs

    def fetch_pairs(self):
        return self._pairs


class RecordingNotifier:
    def __init__(self):
        self.messages = []

    def send(self, message):
        self.messages.append(message)
        return True


def _make_bot(tmp_path, pairs, alert_on_first_run=True):
    cfg = Config()
    cfg.state_file = str(tmp_path / "state.json")
    cfg.alert_on_first_run = alert_on_first_run
    bot = ListingBot.__new__(ListingBot)  # bypass __init__ network setup
    from bot.detector import StockDetector
    from bot.state import SeenStore

    bot.config = cfg
    bot.detector = StockDetector()
    bot.store = SeenStore(cfg.state_file)
    bot.notifier = RecordingNotifier()
    bot.clients = [FakeClient(pairs)]
    return bot


def test_alerts_on_new_stock(tmp_path):
    pairs = [
        Pair("fake", "TSLAX_USDT", "TSLAX", "USDT"),
        Pair("fake", "BTC_USDT", "BTC", "USDT"),
    ]
    bot = _make_bot(tmp_path, pairs, alert_on_first_run=True)
    alerted = bot.run_once()
    assert len(alerted) == 1
    assert alerted[0].base == "TSLAX"
    assert len(bot.notifier.messages) == 1


def test_no_duplicate_alert(tmp_path):
    pairs = [Pair("fake", "TSLAX_USDT", "TSLAX", "USDT")]
    bot = _make_bot(tmp_path, pairs, alert_on_first_run=True)
    bot.run_once()
    bot.run_once()  # same pairs again
    assert len(bot.notifier.messages) == 1


def test_first_run_suppression(tmp_path):
    pairs = [Pair("fake", "TSLAX_USDT", "TSLAX", "USDT")]
    bot = _make_bot(tmp_path, pairs, alert_on_first_run=False)
    alerted = bot.run_once()
    assert alerted == []
    assert bot.notifier.messages == []

    # A genuinely new stock listing on the next cycle DOES alert.
    bot.clients = [FakeClient(pairs + [Pair("fake", "NVDAX_USDT", "NVDAX", "USDT")])]
    alerted = bot.run_once()
    assert len(alerted) == 1
    assert alerted[0].base == "NVDAX"
