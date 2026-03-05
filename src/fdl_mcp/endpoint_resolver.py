from __future__ import annotations

from dataclasses import dataclass

from .config import ServicePathMode


@dataclass(frozen=True)
class EndpointResolver:
    base_url: str
    service_path_mode: ServicePathMode = "auto"

    def resolve(self, endpoint_path: str) -> str:
        path = endpoint_path if endpoint_path.startswith("/") else f"/{endpoint_path}"
        return f"{self.base_url}{path}"

    def data_service_candidates(self, app_id: str, api_path: str) -> list[str]:
        sanitized = api_path.lstrip("/")
        new_path = f"/service/{app_id}/{sanitized}"
        old_path = f"/service/publish/{app_id}/{sanitized}"

        if self.service_path_mode == "new":
            return [new_path]
        if self.service_path_mode == "legacy":
            return [old_path]
        return [new_path, old_path]

