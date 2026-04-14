from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import dataclass
from typing import Any

import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from .auth import AuthProvider
from .endpoint_resolver import EndpointResolver
from .errors import FDLError

TRANSIENT_STATUS = {408, 429, 500, 502, 503, 504}


@dataclass
class FDLClient:
    resolver: EndpointResolver
    auth_provider: AuthProvider
    timeout_ms: int = 10_000
    retry_max: int = 2
    transport: httpx.AsyncBaseTransport | None = None
    encrypt_mode: str = "none"
    encrypt_key: str | None = None

    def _encrypt_payload(self, body: dict[str, Any] | list[Any] | str | None) -> str | dict[str, Any] | list[Any] | None:
        if body is None or self.encrypt_mode == "none":
            return body
        if self.encrypt_mode != "aes":
            raise FDLError(
                code="FDL_ENCRYPT_UNSUPPORTED",
                message=f"Unsupported encrypt mode: {self.encrypt_mode}",
            )
        if not self.encrypt_key:
            raise FDLError(
                code="FDL_ENCRYPT_MISSING_KEY",
                message="FDL encryption key is missing",
            )
        text = body if isinstance(body, str) else httpx.Request("POST", "http://local", json=body).content.decode("utf-8")
        key = self.encrypt_key.encode("utf-8")
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            encrypted = cipher.encrypt(pad(text.encode("utf-8"), AES.block_size))
        except ValueError as exc:
            raise FDLError(
                code="FDL_ENCRYPT_INVALID_CONFIG",
                message="Invalid AES encryption configuration",
                details={"error": str(exc)},
            ) from exc
        return base64.b64encode(encrypted).decode("utf-8")

    def _decrypt_payload(self, body: str) -> Any:
        if self.encrypt_mode == "none":
            return {"raw": body}
        if self.encrypt_mode != "aes":
            raise FDLError(
                code="FDL_ENCRYPT_UNSUPPORTED",
                message=f"Unsupported encrypt mode: {self.encrypt_mode}",
            )
        if not self.encrypt_key:
            raise FDLError(
                code="FDL_ENCRYPT_MISSING_KEY",
                message="FDL encryption key is missing",
            )
        key = self.encrypt_key.encode("utf-8")
        try:
            cipher = AES.new(key, AES.MODE_ECB)
            decrypted = unpad(cipher.decrypt(base64.b64decode(body)), AES.block_size).decode("utf-8")
        except ValueError as exc:
            raise FDLError(
                code="FDL_ENCRYPT_INVALID_PAYLOAD",
                message="Failed to decrypt encrypted response payload",
                details={"error": str(exc)},
            ) from exc
        try:
            return json.loads(decrypted)
        except ValueError:
            return {"raw": decrypted}

    async def request_json(
        self,
        method: str,
        endpoint_path: str,
        *,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | list[Any] | str | None = None,
    ) -> tuple[Any, int, str]:
        url = self.resolver.resolve(endpoint_path)
        timeout = self.timeout_ms / 1000.0

        last_exc: Exception | None = None
        for attempt in range(self.retry_max + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout, transport=self.transport) as client:
                    request_kwargs: dict[str, Any] = {
                        "method": method.upper(),
                        "url": url,
                        "params": query,
                        "headers": headers,
                    }
                    request_body = body
                    if headers and headers.get("fdl-encrypt") == "encrypted":
                        request_body = self._encrypt_payload(body)
                    if isinstance(request_body, str):
                        request_kwargs["content"] = request_body
                    elif request_body is not None:
                        request_kwargs["json"] = request_body
                    request = client.build_request(**request_kwargs)
                    self.auth_provider.apply(request)
                    response = await client.send(request)
            except httpx.HTTPError as exc:
                last_exc = exc
                if attempt < self.retry_max:
                    await asyncio.sleep(0.2 * (2**attempt))
                    continue
                raise FDLError(
                    code="FDL_HTTP_TRANSPORT",
                    message="Transport error while calling FDL",
                    details={"endpoint": endpoint_path, "error": str(exc)},
                ) from exc

            if response.status_code in TRANSIENT_STATUS and attempt < self.retry_max:
                await asyncio.sleep(0.2 * (2**attempt))
                continue

            if 200 <= response.status_code < 300:
                data = self._parse_response(response)
                return data, response.status_code, endpoint_path

            if response.status_code in {401, 403}:
                raise FDLError(
                    code=f"FDL_AUTH_HTTP_{response.status_code}",
                    message="Authentication failed against FDL",
                    status_code=response.status_code,
                    details={"endpoint": endpoint_path, "body": self._safe_text(response)},
                )

            if response.status_code == 404:
                raise FDLError(
                    code="FDL_HTTP_404",
                    message="Resource not found in FDL",
                    status_code=response.status_code,
                    details={"endpoint": endpoint_path, "body": self._safe_text(response)},
                )

            if 400 <= response.status_code < 500:
                raise FDLError(
                    code="FDL_HTTP_4XX",
                    message="Client error returned by FDL",
                    status_code=response.status_code,
                    details={"endpoint": endpoint_path, "body": self._safe_text(response)},
                )

            raise FDLError(
                code="FDL_HTTP_5XX",
                message="Server error returned by FDL",
                status_code=response.status_code,
                details={"endpoint": endpoint_path, "body": self._safe_text(response)},
            )

        raise FDLError(
            code="FDL_HTTP_UNKNOWN",
            message="Unknown HTTP failure",
            details={"endpoint": endpoint_path, "error": str(last_exc) if last_exc else ""},
        )

    async def call_data_service(
        self,
        app_id: str,
        api_path: str,
        method: str,
        *,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | list[Any] | str | None = None,
    ) -> tuple[Any, int, str]:
        last_error: FDLError | None = None
        for endpoint_path in self.resolver.data_service_candidates(app_id, api_path):
            try:
                return await self.request_json(
                    method,
                    endpoint_path,
                    query=query,
                    headers=headers,
                    body=body,
                )
            except FDLError as err:
                last_error = err
                if err.status_code == 404:
                    continue
                raise
        if last_error:
            raise last_error
        raise FDLError(
            code="FDL_HTTP_404",
            message="No data service path candidate succeeded",
            status_code=404,
            details={"app_id": app_id, "api_path": api_path},
        )

    async def request_fdl_dev(
        self,
        method: str,
        endpoint_path: str,
        *,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | list[Any] | str | None = None,
        encrypted: bool = False,
    ) -> tuple[Any, int, str]:
        headers = {
            "accept": "application/json, text/plain, */*",
            "x-requested-with": "XMLHttpRequest",
            "fdl-encrypt": "encrypted" if encrypted else "plaintext",
        }
        if body is not None:
            headers["content-type"] = "application/json"
        return await self.request_json(
            method,
            endpoint_path,
            query=query,
            headers=headers,
            body=body,
        )

    def _parse_response(self, response: httpx.Response) -> Any:
        if response.headers.get("alreadyencrypted") == "true":
            return self._decrypt_payload(response.text)
        try:
            return response.json()
        except ValueError:
            return {"raw": response.text}

    @staticmethod
    def _safe_text(response: httpx.Response, max_chars: int = 500) -> str:
        text = response.text
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 3] + "..."

