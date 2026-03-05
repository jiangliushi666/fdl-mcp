from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any

import httpx

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

    async def request_json(
        self,
        method: str,
        endpoint_path: str,
        *,
        query: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        body: dict[str, Any] | None = None,
    ) -> tuple[Any, int, str]:
        url = self.resolver.resolve(endpoint_path)
        timeout = self.timeout_ms / 1000.0

        last_exc: Exception | None = None
        for attempt in range(self.retry_max + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout, transport=self.transport) as client:
                    request = client.build_request(
                        method=method.upper(),
                        url=url,
                        params=query,
                        headers=headers,
                        json=body,
                    )
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
        body: dict[str, Any] | None = None,
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

    @staticmethod
    def _parse_response(response: httpx.Response) -> Any:
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

