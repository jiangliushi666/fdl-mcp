from __future__ import annotations

from typing import Any

SENSITIVE_KEYS = {
    "secret",
    "token",
    "authorization",
    "appcode",
    "password",
    "fdl_secret",
    "fdl_fine_auth_token",
}


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return lowered in SENSITIVE_KEYS or "token" in lowered or "secret" in lowered


def redact_value(value: Any) -> Any:
    if isinstance(value, dict):
        out: dict[str, Any] = {}
        for k, v in value.items():
            if _is_sensitive_key(str(k)):
                out[k] = "***REDACTED***"
            else:
                out[k] = redact_value(v)
        return out
    if isinstance(value, list):
        return [redact_value(v) for v in value]
    return value


def summarize_params(value: Any, max_length: int = 512) -> str:
    redacted = redact_value(value)
    text = str(redacted)
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."

