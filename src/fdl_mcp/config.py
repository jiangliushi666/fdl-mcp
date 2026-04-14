from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal


AuthMode = Literal["aksk", "appcode", "fine_auth_token", "none"]
ServicePathMode = Literal["auto", "new", "legacy"]
EncryptMode = Literal["none", "aes"]


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


def _read_bool_env(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _extract_cookie_value(cookie_header: str, name: str) -> str | None:
    for part in cookie_header.split(";"):
        item = part.strip()
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        if key.strip() == name:
            return value.strip()
    return None


def _normalize_browser_cookie(raw: str) -> str:
    return "; ".join(part.strip() for part in raw.split(";") if part.strip())


def _build_chrome_session_settings(page_data: dict[str, Any], current: "FDLSettings") -> "FDLSettings":
    base_url = str(page_data.get("origin") or "").rstrip("/")
    cookie_header = _normalize_browser_cookie(str(page_data.get("cookie") or ""))
    token = _extract_cookie_value(cookie_header, "fine_auth_token")
    encrypt_key = str(page_data.get("frontSeed") or "").strip() or None
    page_url = str(page_data.get("href") or "").strip() or None
    return FDLSettings(
        base_url=base_url,
        auth_mode="fine_auth_token",
        client_id=current.client_id,
        secret=current.secret,
        appcode=current.appcode,
        fine_auth_token=token,
        fine_auth_cookie=cookie_header or None,
        timeout_ms=current.timeout_ms,
        retry_max=current.retry_max,
        service_path_mode=current.service_path_mode,
        encrypt_mode="aes",
        encrypt_key=encrypt_key,
        chrome_session_mode=True,
        chrome_session_page_url=page_url,
        allowed_work_ids=current.allowed_work_ids,
        allowed_work_names=current.allowed_work_names,
        allowed_tools=current.allowed_tools,
        rate_limit_per_min=current.rate_limit_per_min,
        idempotency_ttl_sec=current.idempotency_ttl_sec,
    )


@dataclass(frozen=True)
class FDLSettings:
    base_url: str
    auth_mode: AuthMode
    client_id: str | None
    secret: str | None
    appcode: str | None
    fine_auth_token: str | None
    fine_auth_cookie: str | None
    timeout_ms: int
    retry_max: int
    service_path_mode: ServicePathMode
    encrypt_mode: EncryptMode
    encrypt_key: str | None
    chrome_session_mode: bool
    chrome_session_page_url: str | None
    allowed_work_ids: set[str]
    allowed_work_names: set[str]
    allowed_tools: set[str]
    rate_limit_per_min: int
    idempotency_ttl_sec: int

    @classmethod
    def from_env(cls) -> "FDLSettings":
        fine_auth_cookie = _normalize_browser_cookie(os.getenv("FDL_FINE_AUTH_COOKIE", "")) or None
        fine_auth_token = os.getenv("FDL_FINE_AUTH_TOKEN")
        if not fine_auth_token and fine_auth_cookie:
            fine_auth_token = _extract_cookie_value(fine_auth_cookie, "fine_auth_token")
        return cls(
            base_url=os.getenv("FDL_BASE_URL", "").rstrip("/"),
            auth_mode=(os.getenv("FDL_AUTH_MODE", "aksk").strip() or "aksk"),  # type: ignore[arg-type]
            client_id=os.getenv("FDL_CLIENT_ID"),
            secret=os.getenv("FDL_SECRET"),
            appcode=os.getenv("FDL_APPCODE"),
            fine_auth_token=fine_auth_token,
            fine_auth_cookie=fine_auth_cookie,
            timeout_ms=_read_int_env("FDL_TIMEOUT_MS", 10_000),
            retry_max=_read_int_env("FDL_RETRY_MAX", 2),
            service_path_mode=(os.getenv("FDL_SERVICE_PATH_MODE", "auto").strip() or "auto"),  # type: ignore[arg-type]
            encrypt_mode=(os.getenv("FDL_ENCRYPT_MODE", "none").strip() or "none"),  # type: ignore[arg-type]
            encrypt_key=os.getenv("FDL_ENCRYPT_KEY"),
            chrome_session_mode=_read_bool_env("FDL_CHROME_SESSION_MODE", False),
            chrome_session_page_url=(os.getenv("FDL_CHROME_SESSION_PAGE_URL", "").strip() or None),
            allowed_work_ids=_read_csv_env("FDL_ALLOWED_WORK_IDS"),
            allowed_work_names=_read_csv_env("FDL_ALLOWED_WORK_NAMES"),
            allowed_tools=_read_csv_env("FDL_ALLOWED_TOOLS"),
            rate_limit_per_min=_read_int_env("FDL_RATE_LIMIT_PER_MIN", 120),
            idempotency_ttl_sec=_read_int_env("FDL_IDEMPOTENCY_TTL_SEC", 600),
        )

    @classmethod
    def from_chrome_session_payload(cls, page_data: dict[str, Any]) -> "FDLSettings":
        return _build_chrome_session_settings(page_data, cls.from_env())

    def validate(self) -> None:
        if not self.base_url:
            raise ValueError("FDL_BASE_URL is required")
        if self.auth_mode not in {"aksk", "appcode", "fine_auth_token", "none"}:
            raise ValueError("FDL_AUTH_MODE must be one of: aksk, appcode, fine_auth_token, none")
        if self.service_path_mode not in {"auto", "new", "legacy"}:
            raise ValueError("FDL_SERVICE_PATH_MODE must be one of: auto, new, legacy")
        if self.encrypt_mode not in {"none", "aes"}:
            raise ValueError("FDL_ENCRYPT_MODE must be one of: none, aes")

        if self.auth_mode == "aksk":
            if not self.client_id or not self.secret:
                raise ValueError("FDL_CLIENT_ID and FDL_SECRET are required for aksk mode")
        elif self.auth_mode == "appcode":
            if not self.appcode:
                raise ValueError("FDL_APPCODE is required for appcode mode")
        elif self.auth_mode == "fine_auth_token":
            if not self.fine_auth_token:
                raise ValueError("FDL_FINE_AUTH_TOKEN is required for fine_auth_token mode")

        if self.encrypt_mode == "aes" and not self.encrypt_key:
            raise ValueError("FDL_ENCRYPT_KEY is required for aes mode")

