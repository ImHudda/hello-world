"""CLI entry point: ``python -m bot``."""

from __future__ import annotations

import argparse
import logging
import sys

from .config import Config
from .core import ListingBot


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bot",
        description="Watch Gate.io and Binance for new tokenized-stock spot listings.",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="Run a single poll cycle and exit (useful for cron / testing).",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging.",
    )
    args = parser.parse_args(argv)

    _setup_logging(args.verbose)
    config = Config()

    try:
        bot = ListingBot(config)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if args.once:
        alerted = bot.run_once()
        print(f"Cycle complete. {len(alerted)} new stock listing(s) alerted.")
        return 0

    try:
        bot.run_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
