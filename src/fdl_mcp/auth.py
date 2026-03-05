from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass
from typing import Callable, Protocol
from urllib.parse import parse_qsl, urlencode, urlsplit

import httpx

from .config import FDLSettings


class AuthProvider(Protocol):
    def apply(self, request: httpx.Request) -> None:
        ...


def _body_bytes(request: httpx.Request) -> bytes:
    content = request.content
    if content is None:
        return b""
    if isinstance(content, bytes):
        return content
    return str(content).encode("utf-8")


def _canonical_query(query: str) -> str:
    if not query:
        return ""
    pairs = parse_qsl(query, keep_blank_values=True)
    pairs.sort()
    return urlencode(pairs, doseq=True)


@dataclass
class AkSkSignatureAuth:
    client_id: str
    secret: str
    now_fn: Callable[[], float] | None = None

    def _timestamp(self) -> str:
        fn = self.now_fn or time.time
        return str(int(fn()))

    def _build_sign_payload(self, request: httpx.Request, ts: str) -> str:
        split = urlsplit(str(request.url))
        canonical_query = _canonical_query(split.query)
        body_hash = hashlib.sha256(_body_bytes(request)).hexdigest()
        return "\n".join(
            [
                request.method.upper(),
                split.path,
                canonical_query,
                ts,
                body_hash,
            ]
        )

    def apply(self, request: httpx.Request) -> None:
        ts = self._timestamp()
        payload = self._build_sign_payload(request, ts)
        signature = hmac.new(
            self.secret.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        request.headers["X-FDL-Client-Id"] = self.client_id
        request.headers["X-FDL-Timestamp"] = ts
        request.headers["X-FDL-Signature"] = signature
        request.headers["Authorization"] = f"HMAC-SHA256 {self.client_id}:{signature}"


@dataclass
class AppCodeAuth:
    appcode: str

    def apply(self, request: httpx.Request) -> None:
        request.headers["AppCode"] = self.appcode


@dataclass
class FineAuthTokenAuth:
    token: str

    def apply(self, request: httpx.Request) -> None:
        request.headers["Authorization"] = f"Bearer {self.token}"


def build_auth_provider(settings: FDLSettings) -> AuthProvider:
    if settings.auth_mode == "aksk":
        return AkSkSignatureAuth(client_id=settings.client_id or "", secret=settings.secret or "")
    if settings.auth_mode == "appcode":
        return AppCodeAuth(appcode=settings.appcode or "")
    return FineAuthTokenAuth(token=settings.fine_auth_token or "")
