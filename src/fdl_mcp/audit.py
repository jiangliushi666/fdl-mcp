from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any

from .redaction import summarize_params

LOGGER = logging.getLogger("fdl_mcp.audit")


@dataclass
class AuditLogger:
    logger: logging.Logger = LOGGER

    def emit(
        self,
        *,
        trace_id: str,
        caller: str,
        tool_name: str,
        params: dict[str, Any],
        fdl_endpoint: str,
        status_code: int | None,
        latency_ms: int,
        error_code: str | None = None,
    ) -> None:
        event = {
            "trace_id": trace_id,
            "caller": caller,
            "tool_name": tool_name,
            "params": summarize_params(params),
            "fdl_endpoint": fdl_endpoint,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "error_code": error_code,
        }
        self.logger.info(json.dumps(event, ensure_ascii=True))

