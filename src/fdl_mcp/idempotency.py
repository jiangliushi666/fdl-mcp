from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class IdempotencyStore:
    ttl_sec: int
    _store: dict[str, tuple[float, Any]] = field(default_factory=dict)

    def _cleanup(self) -> None:
        now = time.monotonic()
        expired = [k for k, (ts, _) in self._store.items() if now - ts > self.ttl_sec]
        for key in expired:
            self._store.pop(key, None)

    def get(self, key: str) -> Any | None:
        self._cleanup()
        item = self._store.get(key)
        if not item:
            return None
        return item[1]

    def set(self, key: str, value: Any) -> None:
        self._cleanup()
        self._store[key] = (time.monotonic(), value)

