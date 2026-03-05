from __future__ import annotations

import time
from collections import defaultdict, deque
from dataclasses import dataclass, field

from .errors import FDLError


@dataclass
class PolicyGuard:
    allowed_work_ids: set[str]
    allowed_work_names: set[str]
    allowed_tools: set[str]
    rate_limit_per_min: int
    _timestamps: dict[tuple[str, str], deque[float]] = field(
        default_factory=lambda: defaultdict(deque)
    )

    def check_tool(self, tool_name: str) -> None:
        if self.allowed_tools and tool_name not in self.allowed_tools:
            raise FDLError(
                code="FDL_POLICY_TOOL_BLOCKED",
                message=f"Tool {tool_name} is not allowed",
                status_code=403,
            )

    def check_work_target(self, work_id: str | None = None, work_name: str | None = None) -> None:
        if work_id and self.allowed_work_ids and work_id not in self.allowed_work_ids:
            raise FDLError(
                code="FDL_POLICY_WORKID_BLOCKED",
                message=f"work_id {work_id} is not allowed",
                status_code=403,
            )
        if work_name and self.allowed_work_names and work_name not in self.allowed_work_names:
            raise FDLError(
                code="FDL_POLICY_WORKNAME_BLOCKED",
                message=f"work_name {work_name} is not allowed",
                status_code=403,
            )

    def check_rate_limit(self, caller: str, tool_name: str) -> None:
        key = (caller, tool_name)
        now = time.monotonic()
        queue = self._timestamps[key]

        cutoff = now - 60.0
        while queue and queue[0] < cutoff:
            queue.popleft()

        if len(queue) >= self.rate_limit_per_min:
            raise FDLError(
                code="FDL_POLICY_RATE_LIMIT",
                message=f"Rate limit exceeded for caller={caller}, tool={tool_name}",
                status_code=429,
            )
        queue.append(now)

