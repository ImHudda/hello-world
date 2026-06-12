"""Tests for the tokenized-stock detector."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bot.detector import StockDetector  # noqa: E402


def test_known_ticker_matches():
    det = StockDetector()
    assert det.classify("TSLA").is_stock
    assert det.classify("AAPL").is_stock
    assert det.classify("SPACEX").is_stock


def test_tokenized_suffix_matches():
    det = StockDetector()
    m = det.classify("TSLAX")
    assert m.is_stock
    assert m.ticker == "TSLA"
    assert det.classify("NVDAX").is_stock


def test_dotted_suffix_normalizes():
    det = StockDetector()
    assert det.classify("AAPL.X").is_stock


def test_keyword_matches():
    det = StockDetector()
    assert det.classify("XSTOCK").is_stock
    assert det.classify("MYSTOCK").is_stock


def test_non_stock_does_not_match():
    det = StockDetector()
    assert not det.classify("BTC").is_stock
    assert not det.classify("ETH").is_stock
    assert not det.classify("USDT").is_stock
    # "X" suffix alone should not trigger when the stem is unknown.
    assert not det.classify("BTCX").is_stock


def test_extra_tickers():
    det = StockDetector(extra_tickers=["FOO"])
    assert det.classify("FOO").is_stock
    assert det.classify("FOOX").is_stock


def test_empty_input():
    det = StockDetector()
    assert not det.classify("").is_stock
