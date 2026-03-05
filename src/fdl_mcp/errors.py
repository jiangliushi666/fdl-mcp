from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class FDLError(Exception):
    code: str
    message: str
    status_code: int | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return f"{self.code}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "status_code": self.status_code,
                "details": self.details,
            }
        }

