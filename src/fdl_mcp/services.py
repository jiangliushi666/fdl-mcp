from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .client import FDLClient
from .errors import FDLError


@dataclass
class TaskService:
    client: FDLClient

    async def execute_work_by_id(self, work_id: str, payload: dict[str, Any] | None = None) -> tuple[Any, int, str]:
        body = {"workId": work_id}
        if payload is not None:
            body["payload"] = payload
        return await self.client.request_json(
            "POST",
            "/decision/sp/client/api/fdl/workId/execute",
            body=body,
        )

    async def execute_work_by_name(
        self, work_name: str, payload: dict[str, Any] | None = None
    ) -> tuple[Any, int, str]:
        body = {"workName": work_name}
        if payload is not None:
            body["payload"] = payload
        return await self.client.request_json(
            "POST",
            "/decision/sp/client/api/fdl/workName/execute",
            body=body,
        )

    async def get_record(self, record_id: str) -> tuple[Any, int, str]:
        return await self.client.request_json(
            "GET",
            "/decision/sp/client/api/fdl/record/info",
            query={"recordId": record_id},
        )

    async def list_records(
        self,
        *,
        work_id: str | None = None,
        work_name: str | None = None,
        status: str | None = None,
        time_from: str | None = None,
        time_to: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[Any, int, str]:
        query: dict[str, Any] = {"page": page, "pageSize": page_size}
        if work_id:
            query["workId"] = work_id
        if work_name:
            query["workName"] = work_name
        if status:
            query["status"] = status
        if time_from:
            query["timeFrom"] = time_from
        if time_to:
            query["timeTo"] = time_to

        try:
            return await self.client.request_json(
                "GET",
                "/decision/sp/client/api/fdl/record/list",
                query=query,
            )
        except FDLError as err:
            if err.status_code != 404:
                raise
            return await self.client.request_json(
                "GET",
                "/decision/sp/client/api/fdl/records/list",
                query=query,
            )

    async def terminate_records(self, record_ids: list[str]) -> tuple[Any, int, str]:
        if not record_ids:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="record_ids cannot be empty",
                status_code=400,
            )
        return await self.client.request_json(
            "POST",
            "/decision/sp/client/api/fdl/records/terminate",
            body={"recordIds": record_ids},
        )

    async def terminate_work(
        self,
        *,
        work_id: str | None = None,
        work_name: str | None = None,
    ) -> tuple[Any, int, str]:
        if not work_id and not work_name:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="Either work_id or work_name is required",
                status_code=400,
            )

        records_data, _, _ = await self.list_records(
            work_id=work_id,
            work_name=work_name,
            status="RUNNING",
            page=1,
            page_size=200,
        )
        record_ids = self._extract_record_ids(records_data)
        if not record_ids:
            return {"terminated": 0, "message": "No running records found"}, 200, "/decision/sp/client/api/fdl/records/terminate"

        result, status_code, endpoint = await self.terminate_records(record_ids)
        return {
            "terminated": len(record_ids),
            "record_ids": record_ids,
            "result": result,
        }, status_code, endpoint

    @staticmethod
    def _extract_record_ids(records_data: Any) -> list[str]:
        if isinstance(records_data, list):
            source = records_data
        elif isinstance(records_data, dict):
            source = (
                records_data.get("records")
                or records_data.get("data", {}).get("records")
                or records_data.get("data", {}).get("items")
                or records_data.get("items")
                or []
            )
        else:
            source = []

        out: list[str] = []
        for item in source:
            if not isinstance(item, dict):
                continue
            value = item.get("recordId") or item.get("id")
            if value is not None:
                out.append(str(value))
        return out

