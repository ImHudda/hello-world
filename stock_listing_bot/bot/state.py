"""Persistence of already-seen pair keys, so restarts don't re-alert."""

from __future__ import annotations

import json
import logging
import os
import tempfile

log = logging.getLogger(__name__)


class SeenStore:
    """A set of pair keys persisted to a JSON file."""

    def __init__(self, path: str) -> None:
        self._path = path
        self._seen: set[str] = set()
        self._loaded = False

    @property
    def is_empty(self) -> bool:
        return len(self._seen) == 0

    def load(self) -> None:
        self._loaded = True
        if not os.path.exists(self._path):
            return
        try:
            with open(self._path, encoding="utf-8") as fh:
                data = json.load(fh)
            self._seen = set(data.get("seen", []))
        except (OSError, ValueError) as exc:
            log.warning("Could not read state file %s: %s", self._path, exc)

    def __contains__(self, key: str) -> bool:
        return key in self._seen

    def add(self, key: str) -> None:
        self._seen.add(key)

    def update(self, keys) -> None:
        self._seen.update(keys)

    def save(self) -> None:
        """Atomically write state to disk."""
        directory = os.path.dirname(os.path.abspath(self._path)) or "."
        try:
            fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump({"seen": sorted(self._seen)}, fh)
            os.replace(tmp, self._path)
        except OSError as exc:
            log.error("Could not write state file %s: %s", self._path, exc)
