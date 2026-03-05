from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


AuthMode = Literal["aksk", "appcode", "fine_auth_token"]
ServicePathMode = Literal["auto", "new", "legacy"]


def _read_csv_env(name: str) -> set[str]:
    raw = os.getenv(name, "").strip()
    if not raw:
        return set()
    return {part.strip() for part in raw.split(",") if part.strip()}


def _read_int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


@dataclass(frozen=True)
class FDLSettings:
    base_url: str
    auth_mode: AuthMode
    client_id: str | None
    secret: str | None
    appcode: str | None
    fine_auth_token: str | None
    timeout_ms: int
    retry_max: int
    service_path_mode: ServicePathMode
    allowed_work_ids: set[str]
    allowed_work_names: set[str]
    allowed_tools: set[str]
    rate_limit_per_min: int
    idempotency_ttl_sec: int

    @classmethod
    def from_env(cls) -> "FDLSettings":
        return cls(
            base_url=os.getenv("FDL_BASE_URL", "").rstrip("/"),
            auth_mode=(os.getenv("FDL_AUTH_MODE", "aksk").strip() or "aksk"),  # type: ignore[arg-type]
            client_id=os.getenv("FDL_CLIENT_ID"),
            secret=os.getenv("FDL_SECRET"),
            appcode=os.getenv("FDL_APPCODE"),
            fine_auth_token=os.getenv("FDL_FINE_AUTH_TOKEN"),
            timeout_ms=_read_int_env("FDL_TIMEOUT_MS", 10_000),
            retry_max=_read_int_env("FDL_RETRY_MAX", 2),
            service_path_mode=(os.getenv("FDL_SERVICE_PATH_MODE", "auto").strip() or "auto"),  # type: ignore[arg-type]
            allowed_work_ids=_read_csv_env("FDL_ALLOWED_WORK_IDS"),
            allowed_work_names=_read_csv_env("FDL_ALLOWED_WORK_NAMES"),
            allowed_tools=_read_csv_env("FDL_ALLOWED_TOOLS"),
            rate_limit_per_min=_read_int_env("FDL_RATE_LIMIT_PER_MIN", 120),
            idempotency_ttl_sec=_read_int_env("FDL_IDEMPOTENCY_TTL_SEC", 600),
        )

    def validate(self) -> None:
        if not self.base_url:
            raise ValueError("FDL_BASE_URL is required")
        if self.auth_mode not in {"aksk", "appcode", "fine_auth_token"}:
            raise ValueError("FDL_AUTH_MODE must be one of: aksk, appcode, fine_auth_token")
        if self.service_path_mode not in {"auto", "new", "legacy"}:
            raise ValueError("FDL_SERVICE_PATH_MODE must be one of: auto, new, legacy")

        if self.auth_mode == "aksk":
            if not self.client_id or not self.secret:
                raise ValueError("FDL_CLIENT_ID and FDL_SECRET are required for aksk mode")
        elif self.auth_mode == "appcode":
            if not self.appcode:
                raise ValueError("FDL_APPCODE is required for appcode mode")
        elif self.auth_mode == "fine_auth_token":
            if not self.fine_auth_token:
                raise ValueError("FDL_FINE_AUTH_TOKEN is required for fine_auth_token mode")

