from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any

from mcp.server.fastmcp import FastMCP

from .audit import AuditLogger
from .auth import build_auth_provider
from .client import FDLClient
from .config import FDLSettings
from .endpoint_resolver import EndpointResolver
from .errors import FDLError
from .idempotency import IdempotencyStore
from .policy import PolicyGuard
from .services import TaskService

logging.basicConfig(level=logging.INFO, format="%(message)s")


def _get_caller() -> str:
    return os.getenv("MCP_CALLER", os.getenv("USERNAME", "unknown"))


def _trace_id() -> str:
    return uuid.uuid4().hex


class App:
    def __init__(self) -> None:
        self.settings = FDLSettings.from_env()
        self.settings.validate()
        self.resolver = EndpointResolver(
            base_url=self.settings.base_url,
            service_path_mode=self.settings.service_path_mode,
        )
        self.client = FDLClient(
            resolver=self.resolver,
            auth_provider=build_auth_provider(self.settings),
            timeout_ms=self.settings.timeout_ms,
            retry_max=self.settings.retry_max,
        )
        self.tasks = TaskService(self.client)
        self.audit = AuditLogger()
        self.policy = PolicyGuard(
            allowed_work_ids=self.settings.allowed_work_ids,
            allowed_work_names=self.settings.allowed_work_names,
            allowed_tools=self.settings.allowed_tools,
            rate_limit_per_min=self.settings.rate_limit_per_min,
        )
        self.idempotency = IdempotencyStore(self.settings.idempotency_ttl_sec)
        self.mcp = FastMCP("fdl-mcp")
        self._register_tools()

    def _register_tools(self) -> None:
        @self.mcp.tool()
        async def fdl_execute_work_by_id(
            work_id: str,
            payload: dict[str, Any] | None = None,
            idempotency_key: str | None = None,
        ) -> dict[str, Any]:
            tool_name = "fdl_execute_work_by_id"
            params = {"work_id": work_id, "payload": payload, "idempotency_key": idempotency_key}
            return await self._with_audit(
                tool_name=tool_name,
                params=params,
                work_id=work_id,
                call=lambda: self._handle_idempotent(
                    idempotency_key=idempotency_key,
                    operation=lambda: self.tasks.execute_work_by_id(work_id, payload),
                ),
            )

        @self.mcp.tool()
        async def fdl_execute_work_by_name(
            work_name: str,
            payload: dict[str, Any] | None = None,
            idempotency_key: str | None = None,
        ) -> dict[str, Any]:
            tool_name = "fdl_execute_work_by_name"
            params = {"work_name": work_name, "payload": payload, "idempotency_key": idempotency_key}
            return await self._with_audit(
                tool_name=tool_name,
                params=params,
                work_name=work_name,
                call=lambda: self._handle_idempotent(
                    idempotency_key=idempotency_key,
                    operation=lambda: self.tasks.execute_work_by_name(work_name, payload),
                ),
            )

        @self.mcp.tool()
        async def fdl_get_record(record_id: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_get_record",
                params={"record_id": record_id},
                call=lambda: self.tasks.get_record(record_id),
            )

        @self.mcp.tool()
        async def fdl_list_records(
            work_id: str | None = None,
            work_name: str | None = None,
            status: str | None = None,
            time_from: str | None = None,
            time_to: str | None = None,
            page: int = 1,
            page_size: int = 50,
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_list_records",
                params={
                    "work_id": work_id,
                    "work_name": work_name,
                    "status": status,
                    "time_from": time_from,
                    "time_to": time_to,
                    "page": page,
                    "page_size": page_size,
                },
                work_id=work_id,
                work_name=work_name,
                call=lambda: self.tasks.list_records(
                    work_id=work_id,
                    work_name=work_name,
                    status=status,
                    time_from=time_from,
                    time_to=time_to,
                    page=page,
                    page_size=page_size,
                ),
            )

        @self.mcp.tool()
        async def fdl_terminate_records(record_ids: list[str]) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_terminate_records",
                params={"record_ids": record_ids},
                call=lambda: self.tasks.terminate_records(record_ids),
            )

        @self.mcp.tool()
        async def fdl_terminate_work(
            work_id: str | None = None,
            work_name: str | None = None,
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_terminate_work",
                params={"work_id": work_id, "work_name": work_name},
                work_id=work_id,
                work_name=work_name,
                call=lambda: self.tasks.terminate_work(work_id=work_id, work_name=work_name),
            )

        @self.mcp.tool()
        async def fdl_call_data_service(
            app_id: str,
            api_path: str,
            method: str,
            query: dict[str, Any] | None = None,
            headers: dict[str, str] | None = None,
            body: dict[str, Any] | None = None,
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_call_data_service",
                params={
                    "app_id": app_id,
                    "api_path": api_path,
                    "method": method,
                    "query": query,
                    "headers": headers,
                    "body": body,
                },
                call=lambda: self.client.call_data_service(
                    app_id=app_id,
                    api_path=api_path,
                    method=method,
                    query=query,
                    headers=headers,
                    body=body,
                ),
            )

        @self.mcp.tool()
        async def fdl_healthcheck() -> dict[str, Any]:
            return {
                "ok": True,
                "base_url": self.settings.base_url,
                "auth_mode": self.settings.auth_mode,
                "service_path_mode": self.settings.service_path_mode,
                "retry_max": self.settings.retry_max,
                "timeout_ms": self.settings.timeout_ms,
            }

    async def _handle_idempotent(self, idempotency_key: str | None, operation: Any) -> tuple[Any, int, str]:
        if not idempotency_key:
            return await operation()
        cached = self.idempotency.get(idempotency_key)
        if cached is not None:
            data, status_code, endpoint = cached
            if isinstance(data, dict):
                data = {**data, "idempotent_replay": True}
            return data, status_code, endpoint

        result = await operation()
        self.idempotency.set(idempotency_key, result)
        return result

    async def _with_audit(
        self,
        *,
        tool_name: str,
        params: dict[str, Any],
        call: Any,
        work_id: str | None = None,
        work_name: str | None = None,
    ) -> dict[str, Any]:
        trace_id = _trace_id()
        caller = _get_caller()
        start = time.perf_counter()
        endpoint = "unknown"
        status_code: int | None = None
        error_code: str | None = None

        try:
            self.policy.check_tool(tool_name)
            self.policy.check_rate_limit(caller, tool_name)
            self.policy.check_work_target(work_id=work_id, work_name=work_name)

            data, status_code, endpoint = await call()
            return {
                "trace_id": trace_id,
                "ok": True,
                "status_code": status_code,
                "endpoint": endpoint,
                "data": data,
            }
        except FDLError as err:
            status_code = err.status_code
            error_code = err.code
            if endpoint == "unknown":
                endpoint = str(err.details.get("endpoint", "unknown"))
            return {
                "trace_id": trace_id,
                "ok": False,
                **err.to_dict(),
            }
        except Exception as err:
            error_code = "FDL_TASK_UNHANDLED"
            return {
                "trace_id": trace_id,
                "ok": False,
                "error": {
                    "code": "FDL_TASK_UNHANDLED",
                    "message": str(err),
                },
            }
        finally:
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            self.audit.emit(
                trace_id=trace_id,
                caller=caller,
                tool_name=tool_name,
                params=params,
                fdl_endpoint=endpoint,
                status_code=status_code,
                latency_ms=elapsed_ms,
                error_code=error_code,
            )


def main() -> None:
    app = App()
    app.mcp.run()


if __name__ == "__main__":
    main()

