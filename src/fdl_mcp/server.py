from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any, Mapping

from mcp.server.fastmcp import FastMCP

from .audit import AuditLogger
from .auth import build_auth_provider
from .client import FDLClient
from .config import FDLSettings
from .dev_services import DevService
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


def _build_runtime_components(settings: FDLSettings) -> tuple[EndpointResolver, FDLClient, TaskService, DevService]:
    resolver = EndpointResolver(
        base_url=settings.base_url,
        service_path_mode=settings.service_path_mode,
    )
    client = FDLClient(
        resolver=resolver,
        auth_provider=build_auth_provider(settings),
        timeout_ms=settings.timeout_ms,
        retry_max=settings.retry_max,
        encrypt_mode=settings.encrypt_mode,
        encrypt_key=settings.encrypt_key,
    )
    return resolver, client, TaskService(client), DevService(client)


class App:
    def __init__(self) -> None:
        self.settings = FDLSettings.from_env()
        self.settings.validate()
        self.resolver, self.client, self.tasks, self.dev = _build_runtime_components(self.settings)
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
        async def fdl_dev_configure_chrome_session(
            page_data: Mapping[str, Any],
        ) -> dict[str, Any]:
            settings = FDLSettings.from_chrome_session_payload(dict(page_data))
            settings.validate()
            self.settings = settings
            self.resolver, self.client, self.tasks, self.dev = _build_runtime_components(self.settings)
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_configure_chrome_session",
                "data": {
                    "base_url": self.settings.base_url,
                    "auth_mode": self.settings.auth_mode,
                    "encrypt_mode": self.settings.encrypt_mode,
                    "chrome_session_mode": self.settings.chrome_session_mode,
                    "chrome_session_page_url": self.settings.chrome_session_page_url,
                    "has_fine_auth_token": bool(self.settings.fine_auth_token),
                    "has_cookie_header": bool(self.settings.fine_auth_cookie),
                    "has_encrypt_key": bool(self.settings.encrypt_key),
                },
            }

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
        async def fdl_dev_list_connections(connection_type: str = "mysql") -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_list_connections",
                params={"connection_type": connection_type},
                call=lambda: self.dev.list_connections(connection_type),
            )

        @self.mcp.tool()
        async def fdl_dev_get_connection_info(connection_name: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_connection_info",
                params={"connection_name": connection_name},
                call=lambda: self.dev.get_connection_info(connection_name),
            )

        @self.mcp.tool()
        async def fdl_dev_list_connection_schemas(connection_name: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_list_connection_schemas",
                params={"connection_name": connection_name},
                call=lambda: self.dev.list_connection_schemas(connection_name),
            )

        @self.mcp.tool()
        async def fdl_dev_list_table_views(
            connection: str,
            database: str = "",
            schema: str = "",
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_list_table_views",
                params={"connection": connection, "database": database, "schema": schema},
                call=lambda: self.dev.list_table_views(connection, database, schema),
            )

        @self.mcp.tool()
        async def fdl_dev_get_global_params() -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_global_params",
                params={},
                call=self.dev.get_global_params,
            )

        @self.mcp.tool()
        async def fdl_dev_get_development_instance_info(work_id: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_development_instance_info",
                params={"work_id": work_id},
                work_id=work_id,
                call=lambda: self.dev.get_development_instance_info(work_id),
            )

        @self.mcp.tool()
        async def fdl_dev_list_work_versions(work_id: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_list_work_versions",
                params={"work_id": work_id},
                work_id=work_id,
                call=lambda: self.dev.list_work_versions(work_id),
            )

        @self.mcp.tool()
        async def fdl_dev_get_published_work_info(work_id: str, source: str = "") -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_published_work_info",
                params={"work_id": work_id, "source": source},
                work_id=work_id,
                call=lambda: self.dev.get_published_work_info(work_id, source),
            )

        @self.mcp.tool()
        async def fdl_dev_get_catalog_entity_info(work_id: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_catalog_entity_info",
                params={"work_id": work_id},
                work_id=work_id,
                call=lambda: self.dev.get_catalog_entity_info(work_id),
            )

        @self.mcp.tool()
        async def fdl_dev_get_work_development_info(work_id: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_work_development_info",
                params={"work_id": work_id},
                work_id=work_id,
                call=lambda: self.dev.get_work_development_info(work_id),
            )

        @self.mcp.tool()
        async def fdl_dev_list_functions() -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_list_functions",
                params={},
                call=self.dev.list_functions,
            )

        @self.mcp.tool()
        async def fdl_dev_get_downstream(work_id: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_downstream",
                params={"work_id": work_id},
                work_id=work_id,
                call=lambda: self.dev.get_downstream(work_id),
            )

        @self.mcp.tool()
        async def fdl_dev_get_published_instance_info(work_id: str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_published_instance_info",
                params={"work_id": work_id},
                work_id=work_id,
                call=lambda: self.dev.get_published_instance_info(work_id),
            )

        @self.mcp.tool()
        async def fdl_dev_preview_datasource(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_preview_datasource",
                params={"payload": payload},
                call=lambda: self.dev.preview_datasource(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_get_source_fields(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_source_fields",
                params={"payload": payload},
                call=lambda: self.dev.get_source_fields(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_get_target_fields(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_target_fields",
                params={"payload": payload},
                call=lambda: self.dev.get_target_fields(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_refresh_fields(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_refresh_fields",
                params={"payload": payload},
                call=lambda: self.dev.refresh_fields(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_get_field_modifies(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_field_modifies",
                params={"payload": payload},
                call=lambda: self.dev.get_field_modifies(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_get_partition_config(payload: dict[str, Any] | list[Any]) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_get_partition_config",
                params={"payload": payload},
                call=lambda: self.dev.get_partition_config(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_list_template_node_types() -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_list_template_node_types",
                "data": self.dev.list_supported_template_node_types(),
            }

        @self.mcp.tool()
        async def fdl_dev_get_workflow_template_examples() -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_get_workflow_template_examples",
                "data": self.dev.list_workflow_template_examples(),
            }

        @self.mcp.tool()
        async def fdl_dev_validate_workflow_template(template: dict[str, Any]) -> dict[str, Any]:
            parsed_template = self.dev.workflow_template_from_dict(template)
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_validate_workflow_template",
                "data": {
                    "valid": True,
                    "template": self.dev.workflow_template_to_dict(parsed_template),
                },
            }

        @self.mcp.tool()
        async def fdl_dev_build_workflow_template_from_dict(
            name: str,
            nodes: dict[str, dict[str, Any]],
            lines: list[dict[str, Any]] | None = None,
            note: str = "",
            execute_logic: str = "AND",
            disabled: bool = False,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_workflow_template_from_dict",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template_from_dict(
                        name=name,
                        nodes=nodes,
                        lines=lines,
                        note=note,
                        execute_logic=execute_logic,
                        disabled=disabled,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_db_read_node_template(
            datasource_type: str,
            connection_name: str,
            sql: str,
            name: str = "DB表输入",
            x: int = 0,
            y: int = 0,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_db_read_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "read": self.dev.build_db_read_node_template(
                                datasource_type=datasource_type,
                                connection_name=connection_name,
                                sql=sql,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["read"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_api_input_node_template(
            url: str,
            method: str = "GET",
            headers: dict[str, Any] | None = None,
            query: dict[str, Any] | None = None,
            body: Any = None,
            timeout_ms: int = 10000,
            response_mapping: list[dict[str, Any]] | None = None,
            name: str = "API输入",
            x: int = 0,
            y: int = 0,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_api_input_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "api": self.dev.build_api_input_node_template(
                                url=url,
                                method=method,
                                headers=headers,
                                query=query,
                                body=body,
                                timeout_ms=timeout_ms,
                                response_mapping=response_mapping,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["api"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_db_write_node_template(
            datasource_type: str,
            connection_name: str,
            schema: str,
            table: str,
            field_transfer_items: list[dict[str, Any]],
            target_database: str = "",
            target_table_mode: int = 1,
            write_type: int = 5,
            write_node_type: str = "",
            sync_mode: str = "OVERWRITE",
            logical_primary_key: list[str] | None = None,
            update_strategy: int = 0,
            partition_fields: list[str] | None = None,
            partition_config: dict[str, Any] | None = None,
            distribute_config: dict[str, Any] | None = None,
            write_config: dict[str, Any] | None = None,
            name: str = "DB表输出",
            x: int = 286,
            y: int = 0,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_db_write_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "write": self.dev.build_db_write_node_template(
                                datasource_type=datasource_type,
                                connection_name=connection_name,
                                schema=schema,
                                table=table,
                                field_transfer_items=field_transfer_items,
                                target_database=target_database,
                                target_table_mode=target_table_mode,
                                write_type=write_type,
                                write_node_type=write_node_type or None,
                                sync_mode=sync_mode,
                                logical_primary_key=logical_primary_key,
                                update_strategy=update_strategy,
                                partition_fields=partition_fields,
                                partition_config=partition_config,
                                distribute_config=distribute_config,
                                write_config=write_config,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["write"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_param_output_node_template(
            outputs: list[dict[str, Any]],
            name: str = "参数输出",
            x: int = 286,
            y: int = 0,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_param_output_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "output": self.dev.build_param_output_node_template(
                                outputs=outputs,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["output"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_sql_script_node_template(
            sql: str,
            connection_name: str = "",
            datasource_type: str = "",
            name: str = "SQL脚本",
            x: int = 143,
            y: int = 120,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_sql_script_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "sql": self.dev.build_sql_script_node_template(
                                sql=sql,
                                connection_name=connection_name,
                                datasource_type=datasource_type,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["sql"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_python_script_node_template(
            script: str,
            name: str = "Python脚本",
            x: int = 143,
            y: int = 240,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_python_script_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "python": self.dev.build_python_script_node_template(
                                script=script,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["python"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_file_input_node_template(
            path: str,
            file_format: str,
            delimiter: str = ",",
            encoding: str = "utf-8",
            has_header: bool = True,
            sheet_name: str = "",
            name: str = "文件输入",
            x: int = 0,
            y: int = 0,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_file_input_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "file": self.dev.build_file_input_node_template(
                                path=path,
                                file_format=file_format,
                                delimiter=delimiter,
                                encoding=encoding,
                                has_header=has_header,
                                sheet_name=sheet_name,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["file"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_file_output_node_template(
            path: str,
            file_format: str,
            delimiter: str = ",",
            encoding: str = "utf-8",
            include_header: bool = True,
            sheet_name: str = "",
            overwrite: bool = True,
            name: str = "文件输出",
            x: int = 286,
            y: int = 0,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_file_output_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "file": self.dev.build_file_output_node_template(
                                path=path,
                                file_format=file_format,
                                delimiter=delimiter,
                                encoding=encoding,
                                include_header=include_header,
                                sheet_name=sheet_name,
                                overwrite=overwrite,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["file"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_file_transfer_node_template(
            source_path: str,
            target_path: str,
            transfer_mode: str = "COPY",
            overwrite: bool = True,
            name: str = "文件传输",
            x: int = 143,
            y: int = 120,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_file_transfer_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "transfer": self.dev.build_file_transfer_node_template(
                                source_path=source_path,
                                target_path=target_path,
                                transfer_mode=transfer_mode,
                                overwrite=overwrite,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["transfer"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_call_task_node_template(
            called_work_id: str = "",
            called_work_name: str = "",
            name: str = "调用任务",
            x: int = 286,
            y: int = 480,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_call_task_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "call": self.dev.build_call_task_node_template(
                                called_work_id=called_work_id,
                                called_work_name=called_work_name,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["call"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_condition_branch_node_template(
            condition: str,
            name: str = "条件分支",
            x: int = 143,
            y: int = 360,
        ) -> dict[str, Any]:
            node = self.dev.build_condition_branch_node_template(
                condition=condition,
                name=name,
                x=x,
                y=y,
            )
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_condition_branch_node_template",
                "data": {
                    "node_type": node.node_type,
                    "name": node.name,
                    "x": node.x,
                    "y": node.y,
                    "content": node.content,
                    "note": node.note,
                    "execute_logic": node.execute_logic,
                    "disabled": node.disabled,
                },
            }

        @self.mcp.tool()
        async def fdl_dev_build_param_assign_node_template(
            assignments: list[dict[str, Any]],
            name: str = "参数赋值",
            x: int = 286,
            y: int = 360,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_param_assign_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "assign": self.dev.build_param_assign_node_template(
                                assignments=assignments,
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["assign"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_merge_node_template(
            name: str = "汇聚",
            x: int = 429,
            y: int = 360,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_merge_node_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_workflow_template(
                        name=f"{name}示例",
                        nodes={
                            "merge": self.dev.build_merge_node_template(
                                name=name,
                                x=x,
                                y=y,
                            )
                        },
                    )
                )["data_flow"]["nodes"]["merge"],
            }

        @self.mcp.tool()
        async def fdl_dev_build_sql_to_python_template(
            sql: str,
            python_script: str,
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "SQL转Python",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_sql_to_python_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_sql_to_python_template(
                    sql=sql,
                    python_script=python_script,
                    connection_name=connection_name,
                    datasource_type=datasource_type,
                    work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_sql_python_db_template(
            sql: str,
            python_script: str,
            target_connection_name: str,
            target_datasource_type: str,
            target_schema: str,
            target_table: str,
            field_transfer_items: list[dict[str, Any]],
            source_connection_name: str = "",
            source_datasource_type: str = "",
            target_database: str = "",
            target_table_mode: int = 1,
            write_type: int = 5,
            write_node_type: str = "",
            work_name: str = "SQL-Python-DB",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_sql_python_db_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_sql_python_db_template(
                    sql=sql,
                    python_script=python_script,
                    target_connection_name=target_connection_name,
                    target_datasource_type=target_datasource_type,
                    target_schema=target_schema,
                    target_table=target_table,
                    field_transfer_items=field_transfer_items,
                    source_connection_name=source_connection_name,
                    source_datasource_type=source_datasource_type,
                    target_database=target_database,
                    target_table_mode=target_table_mode,
                    write_type=write_type,
                    write_node_type=write_node_type or None,
                    work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_condition_sql_python_template(
            condition: str,
            success_sql: str,
            failure_python_script: str,
            success_connection_name: str = "",
            success_datasource_type: str = "",
            work_name: str = "条件分支链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_condition_sql_python_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_condition_sql_python_template(
                    condition=condition,
                    success_sql=success_sql,
                    failure_python_script=failure_python_script,
                    success_connection_name=success_connection_name,
                    success_datasource_type=success_datasource_type,
                    work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_condition_call_task_template(
            condition: str,
            true_called_work_id: str = "",
            true_called_work_name: str = "",
            false_called_work_id: str = "",
            false_called_work_name: str = "",
            work_name: str = "条件调用任务链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_condition_call_task_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_condition_call_task_template(
                    condition=condition,
                    true_called_work_id=true_called_work_id,
                    true_called_work_name=true_called_work_name,
                    false_called_work_id=false_called_work_id,
                    false_called_work_name=false_called_work_name,
                    work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_condition_param_merge_template(
            condition: str,
            true_assignments: list[dict[str, Any]],
            false_assignments: list[dict[str, Any]],
            work_name: str = "条件参数汇聚链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_condition_param_merge_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_condition_param_merge_template(
                        condition=condition,
                        true_assignments=true_assignments,
                        false_assignments=false_assignments,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_api_to_param_output_template(
            api_url: str,
            output_fields: list[str],
            method: str = "GET",
            headers: dict[str, Any] | None = None,
            query: dict[str, Any] | None = None,
            body: Any = None,
            timeout_ms: int = 10000,
            work_name: str = "API转参数输出",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_api_to_param_output_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_api_to_param_output_template(
                        api_url=api_url,
                        output_fields=output_fields,
                        method=method,
                        headers=headers,
                        query=query,
                        body=body,
                        timeout_ms=timeout_ms,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_join_template(
            left_sql: str,
            right_sql: str,
            left_keys: list[str],
            right_keys: list[str],
            join_type: str = "INNER",
            left_connection_name: str = "",
            left_datasource_type: str = "",
            right_connection_name: str = "",
            right_datasource_type: str = "",
            work_name: str = "数据关联链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_join_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_join_template(
                        left_sql=left_sql,
                        right_sql=right_sql,
                        left_keys=left_keys,
                        right_keys=right_keys,
                        join_type=join_type,
                        left_connection_name=left_connection_name,
                        left_datasource_type=left_datasource_type,
                        right_connection_name=right_connection_name,
                        right_datasource_type=right_datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_data_compare_template(
            left_sql: str,
            right_sql: str,
            compare_keys: list[str],
            include_equal_rows: bool = True,
            left_connection_name: str = "",
            left_datasource_type: str = "",
            right_connection_name: str = "",
            right_datasource_type: str = "",
            work_name: str = "数据比对链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_data_compare_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_data_compare_template(
                        left_sql=left_sql,
                        right_sql=right_sql,
                        compare_keys=compare_keys,
                        include_equal_rows=include_equal_rows,
                        left_connection_name=left_connection_name,
                        left_datasource_type=left_datasource_type,
                        right_connection_name=right_connection_name,
                        right_datasource_type=right_datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_union_template(
            upstream_sqls: list[str],
            union_mode: str = "ALL",
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "上下合并链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_union_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_union_template(
                        upstream_sqls=upstream_sqls,
                        union_mode=union_mode,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_unpivot_template(
            source_sql: str,
            value_fields: list[str],
            index_fields: list[str] | None = None,
            variable_field_name: str = "metric_name",
            value_field_name: str = "metric_value",
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "列转行链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_unpivot_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_unpivot_template(
                        source_sql=source_sql,
                        value_fields=value_fields,
                        index_fields=index_fields,
                        variable_field_name=variable_field_name,
                        value_field_name=value_field_name,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_json_parse_template(
            source_sql: str,
            source_field: str,
            target_fields: list[dict[str, Any]],
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "JSON解析链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_json_parse_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_json_parse_template(
                        source_sql=source_sql,
                        source_field=source_field,
                        target_fields=target_fields,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_row_filter_template(
            source_sql: str,
            condition: str,
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "行过滤链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_row_filter_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_row_filter_template(
                        source_sql=source_sql,
                        condition=condition,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_field_select_template(
            source_sql: str,
            selected_fields: list[dict[str, Any]],
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "字段选择链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_field_select_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_field_select_template(
                        source_sql=source_sql,
                        selected_fields=selected_fields,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_sort_template(
            source_sql: str,
            sort_fields: list[dict[str, Any]],
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "排序链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_sort_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_sort_template(
                        source_sql=source_sql,
                        sort_fields=sort_fields,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_aggregate_template(
            source_sql: str,
            aggregations: list[dict[str, Any]],
            group_fields: list[str] | None = None,
            connection_name: str = "",
            datasource_type: str = "",
            work_name: str = "聚合链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_aggregate_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_aggregate_template(
                        source_sql=source_sql,
                        aggregations=aggregations,
                        group_fields=group_fields,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_file_to_db_template(
            file_path: str,
            file_format: str,
            target_connection_name: str,
            target_datasource_type: str,
            target_schema: str,
            target_table: str,
            field_transfer_items: list[dict[str, Any]],
            delimiter: str = ",",
            encoding: str = "utf-8",
            has_header: bool = True,
            sheet_name: str = "",
            target_database: str = "",
            target_table_mode: int = 1,
            write_type: int = 5,
            write_node_type: str = "",
            sync_mode: str = "OVERWRITE",
            logical_primary_key: list[str] | None = None,
            update_strategy: int = 0,
            partition_fields: list[str] | None = None,
            partition_config: dict[str, Any] | None = None,
            distribute_config: dict[str, Any] | None = None,
            write_config: dict[str, Any] | None = None,
            work_name: str = "文件到数据库",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_file_to_db_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_file_to_db_template(
                        file_path=file_path,
                        file_format=file_format,
                        target_connection_name=target_connection_name,
                        target_datasource_type=target_datasource_type,
                        target_schema=target_schema,
                        target_table=target_table,
                        field_transfer_items=field_transfer_items,
                        delimiter=delimiter,
                        encoding=encoding,
                        has_header=has_header,
                        sheet_name=sheet_name,
                        target_database=target_database,
                        target_table_mode=target_table_mode,
                        write_type=write_type,
                        write_node_type=write_node_type or None,
                        sync_mode=sync_mode,
                        logical_primary_key=logical_primary_key,
                        update_strategy=update_strategy,
                        partition_fields=partition_fields,
                        partition_config=partition_config,
                        distribute_config=distribute_config,
                        write_config=write_config,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_db_to_file_template(
            source_sql: str,
            target_path: str,
            target_file_format: str,
            connection_name: str = "",
            datasource_type: str = "",
            delimiter: str = ",",
            encoding: str = "utf-8",
            include_header: bool = True,
            sheet_name: str = "",
            overwrite: bool = True,
            work_name: str = "数据库到文件",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_db_to_file_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_db_to_file_template(
                        source_sql=source_sql,
                        target_path=target_path,
                        target_file_format=target_file_format,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        delimiter=delimiter,
                        encoding=encoding,
                        include_header=include_header,
                        sheet_name=sheet_name,
                        overwrite=overwrite,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_file_transfer_template(
            source_path: str,
            target_path: str,
            transfer_mode: str = "COPY",
            overwrite: bool = True,
            work_name: str = "文件传输链路",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_file_transfer_template",
                "data": self.dev.workflow_template_to_dict(
                    self.dev.build_file_transfer_template(
                        source_path=source_path,
                        target_path=target_path,
                        transfer_mode=transfer_mode,
                        overwrite=overwrite,
                        work_name=work_name,
                    )
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_render_workflow_templates_batch(
            items: list[dict[str, Any]],
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_render_workflow_templates_batch",
                "data": {
                    "items": self.dev.render_workflow_templates_batch(items),
                },
            }

        @self.mcp.tool()
        async def fdl_dev_save_workflow_templates_batch(
            items: list[dict[str, Any]],
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_save_workflow_templates_batch",
                params={"items": items},
                call=lambda: self.dev.save_workflow_templates_batch(items),
            )

        @self.mcp.tool()
        async def fdl_dev_render_workflow_template(
            template: dict[str, Any],
            work_name: str,
            work_id: str = "",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_render_workflow_template",
                "data": self.dev.build_workflow_from_template(
                    self.dev.workflow_template_from_dict(template),
                    work_name=work_name,
                    work_id=work_id or None,
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_save_workflow_template(
            template: dict[str, Any],
            work_name: str,
            work_id: str = "",
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_save_workflow_template",
                params={
                    "template": template,
                    "work_name": work_name,
                    "work_id": work_id,
                },
                work_id=work_id or None,
                work_name=work_name,
                call=lambda: self.dev.save_workflow_template(
                    template=template,
                    work_name=work_name,
                    work_id=work_id or None,
                ),
            )

        @self.mcp.tool()
        async def fdl_dev_publish_workflow_template(
            template: dict[str, Any],
            work_name: str,
            work_id: str = "",
            describe: str = "",
            sub_work_ids: list[str] | None = None,
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_publish_workflow_template",
                params={
                    "template": template,
                    "work_name": work_name,
                    "work_id": work_id,
                    "describe": describe,
                    "sub_work_ids": sub_work_ids,
                },
                work_id=work_id or None,
                work_name=work_name,
                call=lambda: self.dev.publish_workflow_template(
                    template=template,
                    work_name=work_name,
                    work_id=work_id or None,
                    describe=describe,
                    sub_work_ids=sub_work_ids,
                ),
            )

        @self.mcp.tool()
        async def fdl_dev_build_db_to_db_workflow(
            work_name: str,
            source_connection_name: str,
            source_datasource_type: str,
            source_sql: str,
            target_connection_name: str,
            target_datasource_type: str,
            target_schema: str,
            target_table: str,
            field_transfer_items: list[dict[str, Any]],
            target_database: str = "",
            target_table_mode: int = 1,
            write_type: int = 5,
            write_node_type: str = "",
            sync_mode: str = "OVERWRITE",
            logical_primary_key: list[str] | None = None,
            update_strategy: int = 0,
            partition_fields: list[str] | None = None,
            partition_config: dict[str, Any] | None = None,
            distribute_config: dict[str, Any] | None = None,
            write_config: dict[str, Any] | None = None,
            work_id: str = "",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_db_to_db_workflow",
                "data": self.dev.build_db_to_db_workflow(
                    work_name=work_name,
                    source_connection_name=source_connection_name,
                    source_datasource_type=source_datasource_type,
                    source_sql=source_sql,
                    target_connection_name=target_connection_name,
                    target_datasource_type=target_datasource_type,
                    target_schema=target_schema,
                    target_table=target_table,
                    field_transfer_items=field_transfer_items,
                    target_database=target_database,
                    target_table_mode=target_table_mode,
                    write_type=write_type,
                    write_node_type=write_node_type or None,
                    sync_mode=sync_mode,
                    logical_primary_key=logical_primary_key,
                    update_strategy=update_strategy,
                    partition_fields=partition_fields,
                    partition_config=partition_config,
                    distribute_config=distribute_config,
                    write_config=write_config,
                    work_id=work_id or None,
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_publish_payload(
            save_payload: dict[str, Any],
            describe: str = "",
            sub_work_ids: list[str] | None = None,
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_publish_payload",
                "data": self.dev.build_publish_payload(
                    save_payload,
                    describe=describe,
                    sub_work_ids=sub_work_ids,
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_build_partition_payload(save_payload: dict[str, Any]) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_partition_payload",
                "data": self.dev.build_partition_payload(save_payload),
            }

        @self.mcp.tool()
        async def fdl_dev_build_field_debug_payload(
            save_payload: dict[str, Any],
            chosen_node_id: str = "",
            preview_type: str = "",
        ) -> dict[str, Any]:
            return {
                "trace_id": _trace_id(),
                "ok": True,
                "status_code": 200,
                "endpoint": "local://fdl_dev_build_field_debug_payload",
                "data": self.dev.build_field_debug_payload(
                    save_payload,
                    chosen_node_id=chosen_node_id or None,
                    preview_type=preview_type,
                ),
            }

        @self.mcp.tool()
        async def fdl_dev_prepare_db_to_db_workflow(
            work_name: str,
            source_connection_name: str,
            source_datasource_type: str,
            source_sql: str,
            target_connection_name: str,
            target_datasource_type: str,
            target_schema: str,
            target_table: str,
            field_transfer_items: list[dict[str, Any]],
            target_database: str = "",
            target_table_mode: int = 1,
            write_type: int = 5,
            write_node_type: str = "",
            sync_mode: str = "OVERWRITE",
            logical_primary_key: list[str] | None = None,
            update_strategy: int = 0,
            partition_fields: list[str] | None = None,
            partition_config: dict[str, Any] | None = None,
            distribute_config: dict[str, Any] | None = None,
            write_config: dict[str, Any] | None = None,
            work_id: str = "",
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_prepare_db_to_db_workflow",
                params={
                    "work_name": work_name,
                    "source_connection_name": source_connection_name,
                    "source_datasource_type": source_datasource_type,
                    "source_sql": source_sql,
                    "target_connection_name": target_connection_name,
                    "target_datasource_type": target_datasource_type,
                    "target_schema": target_schema,
                    "target_table": target_table,
                    "field_transfer_items": field_transfer_items,
                    "target_database": target_database,
                    "target_table_mode": target_table_mode,
                    "write_type": write_type,
                    "write_node_type": write_node_type,
                    "sync_mode": sync_mode,
                    "logical_primary_key": logical_primary_key,
                    "update_strategy": update_strategy,
                    "partition_fields": partition_fields,
                    "partition_config": partition_config,
                    "distribute_config": distribute_config,
                    "write_config": write_config,
                    "work_id": work_id,
                },
                work_id=work_id or None,
                call=lambda: self.dev.prepare_db_to_db_workflow(
                    work_name=work_name,
                    source_connection_name=source_connection_name,
                    source_datasource_type=source_datasource_type,
                    source_sql=source_sql,
                    target_connection_name=target_connection_name,
                    target_datasource_type=target_datasource_type,
                    target_schema=target_schema,
                    target_table=target_table,
                    field_transfer_items=field_transfer_items,
                    target_database=target_database,
                    target_table_mode=target_table_mode,
                    write_type=write_type,
                    write_node_type=write_node_type or None,
                    sync_mode=sync_mode,
                    logical_primary_key=logical_primary_key,
                    update_strategy=update_strategy,
                    partition_fields=partition_fields,
                    partition_config=partition_config,
                    distribute_config=distribute_config,
                    write_config=write_config,
                    work_id=work_id or None,
                ),
            )

        @self.mcp.tool()
        async def fdl_dev_save_db_to_db_workflow(
            work_name: str,
            source_connection_name: str,
            source_datasource_type: str,
            source_sql: str,
            target_connection_name: str,
            target_datasource_type: str,
            target_schema: str,
            target_table: str,
            field_transfer_items: list[dict[str, Any]],
            target_database: str = "",
            target_table_mode: int = 1,
            write_type: int = 5,
            write_node_type: str = "",
            sync_mode: str = "OVERWRITE",
            logical_primary_key: list[str] | None = None,
            update_strategy: int = 0,
            partition_fields: list[str] | None = None,
            partition_config: dict[str, Any] | None = None,
            distribute_config: dict[str, Any] | None = None,
            write_config: dict[str, Any] | None = None,
            work_id: str = "",
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_save_db_to_db_workflow",
                params={
                    "work_name": work_name,
                    "source_connection_name": source_connection_name,
                    "source_datasource_type": source_datasource_type,
                    "source_sql": source_sql,
                    "target_connection_name": target_connection_name,
                    "target_datasource_type": target_datasource_type,
                    "target_schema": target_schema,
                    "target_table": target_table,
                    "field_transfer_items": field_transfer_items,
                    "target_database": target_database,
                    "target_table_mode": target_table_mode,
                    "write_type": write_type,
                    "write_node_type": write_node_type,
                    "sync_mode": sync_mode,
                    "logical_primary_key": logical_primary_key,
                    "update_strategy": update_strategy,
                    "partition_fields": partition_fields,
                    "partition_config": partition_config,
                    "distribute_config": distribute_config,
                    "write_config": write_config,
                    "work_id": work_id,
                },
                work_id=work_id or None,
                call=lambda: self.dev.save_db_to_db_workflow(
                    work_name=work_name,
                    source_connection_name=source_connection_name,
                    source_datasource_type=source_datasource_type,
                    source_sql=source_sql,
                    target_connection_name=target_connection_name,
                    target_datasource_type=target_datasource_type,
                    target_schema=target_schema,
                    target_table=target_table,
                    field_transfer_items=field_transfer_items,
                    target_database=target_database,
                    target_table_mode=target_table_mode,
                    write_type=write_type,
                    write_node_type=write_node_type or None,
                    sync_mode=sync_mode,
                    logical_primary_key=logical_primary_key,
                    update_strategy=update_strategy,
                    partition_fields=partition_fields,
                    partition_config=partition_config,
                    distribute_config=distribute_config,
                    write_config=write_config,
                    work_id=work_id or None,
                ),
            )

        @self.mcp.tool()
        async def fdl_dev_publish_db_to_db_workflow(
            work_name: str,
            source_connection_name: str,
            source_datasource_type: str,
            source_sql: str,
            target_connection_name: str,
            target_datasource_type: str,
            target_schema: str,
            target_table: str,
            field_transfer_items: list[dict[str, Any]],
            describe: str = "",
            sub_work_ids: list[str] | None = None,
            target_database: str = "",
            target_table_mode: int = 1,
            write_type: int = 5,
            write_node_type: str = "",
            sync_mode: str = "OVERWRITE",
            logical_primary_key: list[str] | None = None,
            update_strategy: int = 0,
            partition_fields: list[str] | None = None,
            partition_config: dict[str, Any] | None = None,
            distribute_config: dict[str, Any] | None = None,
            write_config: dict[str, Any] | None = None,
            work_id: str = "",
        ) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_publish_db_to_db_workflow",
                params={
                    "work_name": work_name,
                    "source_connection_name": source_connection_name,
                    "source_datasource_type": source_datasource_type,
                    "source_sql": source_sql,
                    "target_connection_name": target_connection_name,
                    "target_datasource_type": target_datasource_type,
                    "target_schema": target_schema,
                    "target_table": target_table,
                    "field_transfer_items": field_transfer_items,
                    "describe": describe,
                    "sub_work_ids": sub_work_ids,
                    "target_database": target_database,
                    "target_table_mode": target_table_mode,
                    "write_type": write_type,
                    "write_node_type": write_node_type,
                    "sync_mode": sync_mode,
                    "logical_primary_key": logical_primary_key,
                    "update_strategy": update_strategy,
                    "partition_fields": partition_fields,
                    "partition_config": partition_config,
                    "distribute_config": distribute_config,
                    "write_config": write_config,
                    "work_id": work_id,
                },
                work_id=work_id or None,
                call=lambda: self.dev.publish_db_to_db_workflow(
                    work_name=work_name,
                    source_connection_name=source_connection_name,
                    source_datasource_type=source_datasource_type,
                    source_sql=source_sql,
                    target_connection_name=target_connection_name,
                    target_datasource_type=target_datasource_type,
                    target_schema=target_schema,
                    target_table=target_table,
                    field_transfer_items=field_transfer_items,
                    describe=describe,
                    sub_work_ids=sub_work_ids,
                    target_database=target_database,
                    target_table_mode=target_table_mode,
                    write_type=write_type,
                    write_node_type=write_node_type or None,
                    sync_mode=sync_mode,
                    logical_primary_key=logical_primary_key,
                    update_strategy=update_strategy,
                    partition_fields=partition_fields,
                    partition_config=partition_config,
                    distribute_config=distribute_config,
                    write_config=write_config,
                    work_id=work_id or None,
                ),
            )

        @self.mcp.tool()
        async def fdl_dev_save_work(payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_save_work",
                params={"payload": payload},
                call=lambda: self.dev.save_work(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_publish_work_check(payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_publish_work_check",
                params={"payload": payload},
                call=lambda: self.dev.publish_work_check(payload),
            )

        @self.mcp.tool()
        async def fdl_dev_publish_work(payload: dict[str, Any] | list[Any] | str) -> dict[str, Any]:
            return await self._with_audit(
                tool_name="fdl_dev_publish_work",
                params={"payload": payload},
                call=lambda: self.dev.publish_work(payload),
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

