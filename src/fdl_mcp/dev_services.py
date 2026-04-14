from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from .client import FDLClient
from .errors import FDLError


@dataclass(frozen=True)
class WorkflowNodeTemplate:
    node_type: str
    name: str
    x: int
    y: int
    content: dict[str, Any]
    note: str = ""
    execute_logic: str = "AND"
    disabled: bool = False


@dataclass(frozen=True)
class WorkflowLineTemplate:
    from_node_key: str
    to_node_key: str
    line_condition: str = "ON_SUCCESS"
    line_type: str = "DEFAULT"


@dataclass(frozen=True)
class DataFlowTemplate:
    name: str
    nodes: dict[str, WorkflowNodeTemplate]
    lines: list[WorkflowLineTemplate] = field(default_factory=list)
    note: str = ""
    execute_logic: str = "AND"
    disabled: bool = False


@dataclass(frozen=True)
class WorkflowTemplate:
    data_flow: DataFlowTemplate


@dataclass(frozen=True)
class SQLToDBWorkflowSpec:
    work_name: str
    source_connection_name: str
    source_datasource_type: str
    source_sql: str
    target_connection_name: str
    target_datasource_type: str
    target_schema: str
    target_table: str
    field_transfer_items: list[dict[str, Any]]
    target_database: str = ""
    target_table_mode: int = 1
    write_type: int = 5
    write_node_type: str | None = None
    sync_mode: str = "OVERWRITE"
    logical_primary_key: list[str] = field(default_factory=list)
    update_strategy: int = 0
    partition_fields: list[str] = field(default_factory=list)
    partition_config: dict[str, Any] | None = None
    distribute_config: dict[str, Any] | None = None
    write_config: dict[str, Any] | None = None
    work_id: str | None = None


DBToDBWorkflowSpec = SQLToDBWorkflowSpec


@dataclass
class DevService:
    client: FDLClient

    async def list_connections(self, connection_type: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            f"/webroot/decision/fdl/dev/conn/fr/get/{connection_type}",
        )

    async def get_connection_info(self, connection_name: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            "/webroot/decision/fdl/dev/conn/info",
            query={"connectionName": connection_name},
        )

    async def list_connection_schemas(self, connection_name: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            "/webroot/decision/fdl/dev/conn/datasource/schemas",
            query={"connectionName": connection_name},
        )

    async def list_table_views(
        self,
        connection: str,
        database: str = "",
        schema: str = "",
    ) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            "/webroot/decision/fdl/dev/datasource/schema/tableViews",
            query={"connection": connection, "database": database, "schema": schema},
        )

    async def get_global_params(self) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            "/webroot/decision/fdl/dev/param/global/query",
        )

    async def get_development_instance_info(self, work_id: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            f"/webroot/decision/fdl/dev/instance/{work_id}/development/info/get",
        )

    async def list_work_versions(self, work_id: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            f"/webroot/decision/fdl/dev/work/{work_id}/versions",
        )

    async def get_published_work_info(self, work_id: str, source: str = "") -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            f"/webroot/decision/fdl/dev/work/info/{work_id}/published",
            query={"source": source},
        )

    async def get_catalog_entity_info(self, work_id: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            "/webroot/decision/fdl/dev/catalog/entity/info",
            query={"workId": work_id},
        )

    async def get_work_development_info(self, work_id: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            f"/webroot/decision/fdl/dev/work/info/{work_id}/development",
        )

    async def list_functions(self) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            "/webroot/decision/fdl/dev/function/list",
        )

    async def get_downstream(self, work_id: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            f"/webroot/decision/fdl/plan/event/{work_id}/downstream/get",
        )

    async def get_published_instance_info(self, work_id: str) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "GET",
            f"/webroot/decision/fdl/dev/instance/{work_id}/published/info/get",
        )

    async def preview_datasource(self, payload: dict[str, Any] | list[Any]) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/datasource/preview",
            body=payload,
            encrypted=True,
        )

    async def get_source_fields(self, payload: dict[str, Any] | list[Any]) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/datasource/field/source",
            body=payload,
            encrypted=True,
        )

    async def get_target_fields(self, payload: dict[str, Any] | list[Any]) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/datasource/field/target",
            body=payload,
            encrypted=True,
        )

    async def refresh_fields(self, payload: dict[str, Any] | list[Any]) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/datasource/field/refresh",
            body=payload,
            encrypted=True,
        )

    async def get_field_modifies(self, payload: dict[str, Any] | list[Any]) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/datasource/field/modifies",
            body=payload,
            encrypted=True,
        )

    async def get_partition_config(self, payload: dict[str, Any] | list[Any]) -> tuple[Any, int, str]:
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/conn/table/conf/partition/get",
            body=payload,
            encrypted=True,
        )

    def build_db_to_db_workflow(
        self,
        *,
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
        write_node_type: str | None = None,
        sync_mode: str = "OVERWRITE",
        logical_primary_key: list[str] | None = None,
        update_strategy: int = 0,
        partition_fields: list[str] | None = None,
        partition_config: dict[str, Any] | None = None,
        distribute_config: dict[str, Any] | None = None,
        write_config: dict[str, Any] | None = None,
        work_id: str | None = None,
    ) -> dict[str, Any]:
        spec = DBToDBWorkflowSpec(
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
            write_node_type=write_node_type,
            sync_mode=sync_mode,
            logical_primary_key=list(logical_primary_key or []),
            update_strategy=update_strategy,
            partition_fields=list(partition_fields or []),
            partition_config=partition_config,
            distribute_config=distribute_config,
            write_config=write_config,
            work_id=work_id,
        )
        return self.build_workflow_from_template(
            self.build_db_to_db_template(spec),
            work_name=spec.work_name,
            work_id=spec.work_id,
        )

    def build_sync_mode_config(
        self,
        *,
        sync_mode: str = "OVERWRITE",
        logical_primary_key: list[str] | None = None,
        update_strategy: int = 0,
        partition_fields: list[str] | None = None,
        partition_config: dict[str, Any] | None = None,
        distribute_config: dict[str, Any] | None = None,
        extra_write_config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        normalized_mode = sync_mode.upper()
        if normalized_mode not in {"OVERWRITE", "APPEND", "UPSERT", "UPDATE", "INSERT"}:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="sync_mode is invalid",
                status_code=400,
            )
        config = {
            "syncMode": normalized_mode,
            "logicalPrimaryKey": list(logical_primary_key or []),
            "updateStrategy": update_strategy,
            "partitionFields": list(partition_fields or []),
            "partitionConfig": partition_config,
            "distributeConfig": distribute_config,
        }
        if extra_write_config:
            config.update(extra_write_config)
        return config

    def build_db_read_node_template(
        self,
        *,
        datasource_type: str,
        connection_name: str,
        sql: str,
        name: str = "DB表输入",
        x: int = 0,
        y: int = 0,
    ) -> WorkflowNodeTemplate:
        return WorkflowNodeTemplate(
            node_type="DB_READ",
            name=name,
            x=x,
            y=y,
            content={
                "fromDatasourceType": datasource_type,
                "fromConnectionName": connection_name,
                "dataBaseConfig": {
                    "type": "SQL",
                    "sql": sql,
                },
                "samples": [
                    {
                        "sampleType": "partRow",
                        "sampleNumbers": 5000,
                    }
                ],
            },
        )

    def build_api_input_node_template(
        self,
        *,
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
    ) -> WorkflowNodeTemplate:
        if not url:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="url cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="API_INPUT",
            name=name,
            x=x,
            y=y,
            content={
                "request": {
                    "method": method.upper(),
                    "url": url,
                    "headers": headers or {},
                    "query": query or {},
                    "body": body,
                    "timeoutMs": timeout_ms,
                },
                "responseMapping": response_mapping or [],
            },
        )

    def build_db_write_node_template(
        self,
        *,
        datasource_type: str,
        connection_name: str,
        schema: str,
        table: str,
        field_transfer_items: list[dict[str, Any]],
        target_database: str = "",
        target_table_mode: int = 1,
        write_type: int = 5,
        write_node_type: str | None = None,
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
    ) -> WorkflowNodeTemplate:
        sync_config = self.build_sync_mode_config(
            sync_mode=sync_mode,
            logical_primary_key=logical_primary_key,
            update_strategy=update_strategy,
            partition_fields=partition_fields,
            partition_config=partition_config,
            distribute_config=distribute_config,
            extra_write_config=write_config,
        )
        return WorkflowNodeTemplate(
            node_type="DB_WRITE",
            name=name,
            x=x,
            y=y,
            content={
                "type": write_node_type or f"{datasource_type.upper()}_WRITE",
                "toDatasourceType": datasource_type,
                "toConnectionName": connection_name,
                "toDatabase": target_database,
                "toSchema": schema,
                "toTableMode": target_table_mode,
                "toTable": table,
                "writeType": write_type,
                "writeConfig": {
                    "logicalPrimaryKey": sync_config["logicalPrimaryKey"],
                    "updateStrategy": sync_config["updateStrategy"],
                    "syncMode": sync_config["syncMode"],
                    **{
                        key: value
                        for key, value in sync_config.items()
                        if key not in {"logicalPrimaryKey", "updateStrategy"}
                    },
                },
                "mapType": "ROW",
                "fieldTransferItems": field_transfer_items,
                "partitionFields": sync_config["partitionFields"],
                "partitionConfig": sync_config["partitionConfig"],
                "distributeConfig": sync_config["distributeConfig"],
                "createSql": "",
                "comment": "",
            },
        )

    def build_param_output_node_template(
        self,
        *,
        outputs: list[dict[str, Any]],
        name: str = "参数输出",
        x: int = 286,
        y: int = 0,
    ) -> WorkflowNodeTemplate:
        if not outputs:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="outputs cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="PARAM_OUTPUT",
            name=name,
            x=x,
            y=y,
            content={
                "outputs": outputs,
            },
        )

    def build_join_node_template(
        self,
        *,
        left_keys: list[str],
        right_keys: list[str],
        join_type: str = "INNER",
        name: str = "数据关联",
        x: int = 143,
        y: int = 120,
    ) -> WorkflowNodeTemplate:
        if not left_keys or not right_keys:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="left_keys and right_keys cannot be empty",
                status_code=400,
            )
        if len(left_keys) != len(right_keys):
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="left_keys and right_keys must have same length",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="JOIN",
            name=name,
            x=x,
            y=y,
            content={
                "joinType": join_type.upper(),
                "leftKeys": left_keys,
                "rightKeys": right_keys,
            },
        )

    def build_data_compare_node_template(
        self,
        *,
        compare_keys: list[str],
        include_equal_rows: bool = True,
        name: str = "数据比对",
        x: int = 143,
        y: int = 240,
    ) -> WorkflowNodeTemplate:
        if not compare_keys:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="compare_keys cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="DATA_COMPARE",
            name=name,
            x=x,
            y=y,
            content={
                "compareKeys": compare_keys,
                "includeEqualRows": include_equal_rows,
            },
        )

    def build_union_node_template(
        self,
        *,
        union_mode: str = "ALL",
        name: str = "上下合并",
        x: int = 143,
        y: int = 360,
    ) -> WorkflowNodeTemplate:
        return WorkflowNodeTemplate(
            node_type="UNION",
            name=name,
            x=x,
            y=y,
            content={
                "unionMode": union_mode.upper(),
            },
        )

    def build_unpivot_node_template(
        self,
        *,
        index_fields: list[str],
        value_fields: list[str],
        variable_field_name: str = "metric_name",
        value_field_name: str = "metric_value",
        name: str = "列转行",
        x: int = 143,
        y: int = 480,
    ) -> WorkflowNodeTemplate:
        if not value_fields:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="value_fields cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="UNPIVOT",
            name=name,
            x=x,
            y=y,
            content={
                "indexFields": index_fields,
                "valueFields": value_fields,
                "variableFieldName": variable_field_name,
                "valueFieldName": value_field_name,
            },
        )

    def build_json_parse_node_template(
        self,
        *,
        source_field: str,
        target_fields: list[dict[str, Any]],
        name: str = "JSON解析",
        x: int = 143,
        y: int = 600,
    ) -> WorkflowNodeTemplate:
        if not source_field:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="source_field cannot be empty",
                status_code=400,
            )
        if not target_fields:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="target_fields cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="JSON_PARSE",
            name=name,
            x=x,
            y=y,
            content={
                "sourceField": source_field,
                "targetFields": target_fields,
            },
        )

    def build_row_filter_node_template(
        self,
        *,
        condition: str,
        name: str = "行过滤",
        x: int = 143,
        y: int = 720,
    ) -> WorkflowNodeTemplate:
        if not condition:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="condition cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="ROW_FILTER",
            name=name,
            x=x,
            y=y,
            content={"condition": condition},
        )

    def build_field_select_node_template(
        self,
        *,
        selected_fields: list[dict[str, Any]],
        name: str = "字段选择",
        x: int = 143,
        y: int = 840,
    ) -> WorkflowNodeTemplate:
        if not selected_fields:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="selected_fields cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="FIELD_SELECT",
            name=name,
            x=x,
            y=y,
            content={"selectedFields": selected_fields},
        )

    def build_sort_node_template(
        self,
        *,
        sort_fields: list[dict[str, Any]],
        name: str = "排序",
        x: int = 143,
        y: int = 960,
    ) -> WorkflowNodeTemplate:
        if not sort_fields:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="sort_fields cannot be empty",
                status_code=400,
            )
        normalized_fields = []
        for item in sort_fields:
            normalized_fields.append(
                {
                    **item,
                    "order": str(item.get("order", "ASC")).upper(),
                }
            )
        return WorkflowNodeTemplate(
            node_type="SORT",
            name=name,
            x=x,
            y=y,
            content={"sortFields": normalized_fields},
        )

    def build_aggregate_node_template(
        self,
        *,
        aggregations: list[dict[str, Any]],
        group_fields: list[str] | None = None,
        name: str = "聚合",
        x: int = 143,
        y: int = 1080,
    ) -> WorkflowNodeTemplate:
        if not aggregations:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="aggregations cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="AGGREGATE",
            name=name,
            x=x,
            y=y,
            content={
                "groupFields": list(group_fields or []),
                "aggregations": aggregations,
            },
        )

    def build_sql_script_node_template(
        self,
        *,
        sql: str,
        connection_name: str = "",
        datasource_type: str = "",
        name: str = "SQL脚本",
        x: int = 143,
        y: int = 120,
    ) -> WorkflowNodeTemplate:
        if not sql:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="sql cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="SQL_SCRIPT",
            name=name,
            x=x,
            y=y,
            content={
                "sql": sql,
                "connectionName": connection_name,
                "datasourceType": datasource_type,
            },
        )

    def build_python_script_node_template(
        self,
        *,
        script: str,
        name: str = "Python脚本",
        x: int = 143,
        y: int = 240,
    ) -> WorkflowNodeTemplate:
        if not script:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="script cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="PYTHON_SCRIPT",
            name=name,
            x=x,
            y=y,
            content={
                "script": script,
                "runtime": "python",
            },
        )

    def build_file_input_node_template(
        self,
        *,
        path: str,
        file_format: str,
        delimiter: str = ",",
        encoding: str = "utf-8",
        has_header: bool = True,
        sheet_name: str = "",
        name: str = "文件输入",
        x: int = 0,
        y: int = 0,
    ) -> WorkflowNodeTemplate:
        if not path:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="path cannot be empty",
                status_code=400,
            )
        if not file_format:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="file_format cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="FILE_INPUT",
            name=name,
            x=x,
            y=y,
            content={
                "path": path,
                "fileFormat": file_format.upper(),
                "delimiter": delimiter,
                "encoding": encoding,
                "hasHeader": has_header,
                "sheetName": sheet_name,
            },
        )

    def build_file_output_node_template(
        self,
        *,
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
    ) -> WorkflowNodeTemplate:
        if not path:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="path cannot be empty",
                status_code=400,
            )
        if not file_format:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="file_format cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="FILE_OUTPUT",
            name=name,
            x=x,
            y=y,
            content={
                "path": path,
                "fileFormat": file_format.upper(),
                "delimiter": delimiter,
                "encoding": encoding,
                "includeHeader": include_header,
                "sheetName": sheet_name,
                "overwrite": overwrite,
            },
        )

    def build_file_transfer_node_template(
        self,
        *,
        source_path: str,
        target_path: str,
        transfer_mode: str = "COPY",
        overwrite: bool = True,
        name: str = "文件传输",
        x: int = 143,
        y: int = 120,
    ) -> WorkflowNodeTemplate:
        if not source_path or not target_path:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="source_path and target_path cannot be empty",
                status_code=400,
            )
        normalized_mode = transfer_mode.upper()
        if normalized_mode not in {"COPY", "MOVE"}:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="transfer_mode is invalid",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="FILE_TRANSFER",
            name=name,
            x=x,
            y=y,
            content={
                "sourcePath": source_path,
                "targetPath": target_path,
                "transferMode": normalized_mode,
                "overwrite": overwrite,
            },
        )

    def build_linear_workflow_template(
        self,
        *,
        name: str,
        node_items: list[tuple[str, WorkflowNodeTemplate]],
        note: str = "",
        execute_logic: str = "AND",
        disabled: bool = False,
    ) -> WorkflowTemplate:
        if not node_items:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="node_items cannot be empty",
                status_code=400,
            )
        nodes = dict(node_items)
        lines = [
            WorkflowLineTemplate(from_node_key=from_key, to_node_key=to_key)
            for (from_key, _), (to_key, _) in zip(node_items, node_items[1:])
        ]
        return self.build_workflow_template(
            name=name,
            nodes=nodes,
            lines=lines,
            note=note,
            execute_logic=execute_logic,
            disabled=disabled,
        )

    def build_workflow_template_from_dict(
        self,
        *,
        name: str,
        nodes: dict[str, dict[str, Any]],
        lines: list[dict[str, Any]] | None = None,
        note: str = "",
        execute_logic: str = "AND",
        disabled: bool = False,
    ) -> WorkflowTemplate:
        return self.workflow_template_from_dict(
            {
                "data_flow": {
                    "name": name,
                    "nodes": nodes,
                    "lines": lines or [],
                    "note": note,
                    "execute_logic": execute_logic,
                    "disabled": disabled,
                }
            }
        )

    @staticmethod
    def list_supported_template_node_types() -> dict[str, Any]:
        return {
            "node_types": [
                {
                    "node_type": "DB_READ",
                    "description": "Read rows from a database connection by SQL.",
                    "required_content_keys": [
                        "fromDatasourceType",
                        "fromConnectionName",
                        "dataBaseConfig",
                        "samples",
                    ],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "API_INPUT",
                    "description": "Read rows from an HTTP API endpoint.",
                    "required_content_keys": ["request", "responseMapping"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "FILE_INPUT",
                    "description": "Read rows from a local or mounted file source.",
                    "required_content_keys": ["path", "fileFormat"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "FILE_OUTPUT",
                    "description": "Write rows into a file target.",
                    "required_content_keys": ["path", "fileFormat"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "FILE_TRANSFER",
                    "description": "Copy or move a file between source and target locations.",
                    "required_content_keys": ["sourcePath", "targetPath", "transferMode"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "DB_WRITE",
                    "description": "Write rows into a target database table.",
                    "required_content_keys": [
                        "type",
                        "toDatasourceType",
                        "toConnectionName",
                        "toSchema",
                        "toTable",
                        "writeType",
                        "fieldTransferItems",
                    ],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "SQL_SCRIPT",
                    "description": "Execute a SQL script node in a workflow.",
                    "required_content_keys": ["sql", "connectionName", "datasourceType"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "PYTHON_SCRIPT",
                    "description": "Execute a Python script node in a workflow.",
                    "required_content_keys": ["script", "runtime"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "CONDITION_BRANCH",
                    "description": "Branch workflow execution by a boolean condition.",
                    "required_content_keys": ["condition"],
                    "line_conditions": ["ON_TRUE", "ON_FALSE"],
                },
                {
                    "node_type": "PARAM_ASSIGN",
                    "description": "Assign workflow variables or parameters for downstream nodes.",
                    "required_content_keys": ["assignments"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "PARAM_OUTPUT",
                    "description": "Emit selected fields as workflow output parameters.",
                    "required_content_keys": ["outputs"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "JOIN",
                    "description": "Join two upstream datasets by key fields.",
                    "required_content_keys": ["joinType", "leftKeys", "rightKeys"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "DATA_COMPARE",
                    "description": "Compare two upstream datasets by key fields.",
                    "required_content_keys": ["compareKeys", "includeEqualRows"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "UNION",
                    "description": "Union rows from multiple upstream branches.",
                    "required_content_keys": ["unionMode"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "UNPIVOT",
                    "description": "Transform columns into rows.",
                    "required_content_keys": ["valueFields", "variableFieldName", "valueFieldName"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "JSON_PARSE",
                    "description": "Parse a JSON field into structured fields.",
                    "required_content_keys": ["sourceField", "targetFields"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "ROW_FILTER",
                    "description": "Filter rows by an expression condition.",
                    "required_content_keys": ["condition"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "FIELD_SELECT",
                    "description": "Select or remap fields for downstream nodes.",
                    "required_content_keys": ["selectedFields"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "SORT",
                    "description": "Sort rows by one or more fields.",
                    "required_content_keys": ["sortFields"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "AGGREGATE",
                    "description": "Aggregate rows by group fields and aggregation functions.",
                    "required_content_keys": ["groupFields", "aggregations"],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "MERGE",
                    "description": "Merge multiple upstream branches back into one path.",
                    "required_content_keys": [],
                    "line_conditions": ["ON_SUCCESS"],
                },
                {
                    "node_type": "CALL_TASK",
                    "description": "Invoke another published workflow by id or name.",
                    "required_content_keys": ["calledWorkId", "calledWorkName"],
                    "line_conditions": ["ON_SUCCESS"],
                },
            ],
            "line_conditions": ["ON_SUCCESS", "ON_TRUE", "ON_FALSE"],
            "line_types": ["DEFAULT"],
        }

    def list_workflow_template_examples(self) -> dict[str, Any]:
        return {
            "examples": {
                "sql_to_python": self.workflow_template_to_dict(
                    self.build_sql_to_python_template(
                        sql="SELECT * FROM demo_source",
                        python_script="print('transform rows')",
                        connection_name="source_conn",
                        datasource_type="mysql",
                        work_name="SQL转Python示例",
                    )
                ),
                "sql_python_db": self.workflow_template_to_dict(
                    self.build_sql_python_db_template(
                        sql="SELECT id, name FROM demo_source",
                        python_script="print('clean and enrich')",
                        source_connection_name="source_conn",
                        source_datasource_type="mysql",
                        target_connection_name="target_conn",
                        target_datasource_type="postgresql",
                        target_schema="public",
                        target_table="demo_target",
                        field_transfer_items=[
                            {
                                "readColumn": {"name": "id", "type": 4},
                                "writeColumn": {"name": "id", "type": 4},
                                "deleted": False,
                            },
                            {
                                "readColumn": {"name": "name", "type": 1},
                                "writeColumn": {"name": "name", "type": 1},
                                "deleted": False,
                            },
                        ],
                        work_name="SQL-Python-DB示例",
                    )
                ),
                "condition_call_task": self.workflow_template_to_dict(
                    self.build_condition_call_task_template(
                        condition="${row_count} > 0",
                        true_called_work_name="sync_non_empty",
                        false_called_work_name="sync_empty",
                        work_name="条件调用任务示例",
                    )
                ),
                "condition_param_merge": self.workflow_template_to_dict(
                    self.build_condition_param_merge_template(
                        condition="${row_count} > 0",
                        true_assignments=[{"name": "has_data", "value": True}],
                        false_assignments=[{"name": "has_data", "value": False}],
                        work_name="条件参数汇聚示例",
                    )
                ),
                "api_to_param_output": self.workflow_template_to_dict(
                    self.build_api_to_param_output_template(
                        api_url="https://api.example.com/orders",
                        output_fields=["order_id", "status"],
                        work_name="API转参数输出示例",
                    )
                ),
                "join_flow": self.workflow_template_to_dict(
                    self.build_join_template(
                        left_sql="SELECT id, amount FROM orders",
                        right_sql="SELECT id, level FROM users",
                        left_keys=["id"],
                        right_keys=["id"],
                        join_type="LEFT",
                        work_name="数据关联示例",
                    )
                ),
                "data_compare_flow": self.workflow_template_to_dict(
                    self.build_data_compare_template(
                        left_sql="SELECT id, updated_at FROM ods_orders",
                        right_sql="SELECT id, updated_at FROM dwd_orders",
                        compare_keys=["id"],
                        include_equal_rows=False,
                        work_name="数据比对示例",
                    )
                ),
                "union_flow": self.workflow_template_to_dict(
                    self.build_union_template(
                        upstream_sqls=[
                            "SELECT id, dt FROM ods_orders_202601",
                            "SELECT id, dt FROM ods_orders_202602",
                        ],
                        union_mode="ALL",
                        work_name="上下合并示例",
                    )
                ),
                "unpivot_flow": self.workflow_template_to_dict(
                    self.build_unpivot_template(
                        source_sql="SELECT id, pv, uv FROM ads_daily_metrics",
                        index_fields=["id"],
                        value_fields=["pv", "uv"],
                        variable_field_name="metric_name",
                        value_field_name="metric_value",
                        work_name="列转行示例",
                    )
                ),
                "json_parse_flow": self.workflow_template_to_dict(
                    self.build_json_parse_template(
                        source_sql="SELECT id, ext_json FROM ods_orders",
                        source_field="ext_json",
                        target_fields=[
                            {"name": "province", "jsonPath": "$.address.province"},
                            {"name": "city", "jsonPath": "$.address.city"},
                        ],
                        work_name="JSON解析示例",
                    )
                ),
                "row_filter_flow": self.workflow_template_to_dict(
                    self.build_row_filter_template(
                        source_sql="SELECT id, amount FROM ods_orders",
                        condition="amount > 100",
                        work_name="行过滤示例",
                    )
                ),
                "field_select_flow": self.workflow_template_to_dict(
                    self.build_field_select_template(
                        source_sql="SELECT id, amount, dt FROM ods_orders",
                        selected_fields=[
                            {"sourceField": "id", "targetField": "order_id"},
                            {"sourceField": "amount", "targetField": "order_amount"},
                        ],
                        work_name="字段选择示例",
                    )
                ),
                "sort_flow": self.workflow_template_to_dict(
                    self.build_sort_template(
                        source_sql="SELECT id, dt, amount FROM ods_orders",
                        sort_fields=[
                            {"field": "dt", "order": "DESC"},
                            {"field": "id", "order": "ASC"},
                        ],
                        work_name="排序示例",
                    )
                ),
                "aggregate_flow": self.workflow_template_to_dict(
                    self.build_aggregate_template(
                        source_sql="SELECT dept, amount FROM ods_orders",
                        group_fields=["dept"],
                        aggregations=[
                            {"field": "amount", "function": "SUM", "as": "total_amount"}
                        ],
                        work_name="聚合示例",
                    )
                ),
                "file_to_db_flow": self.workflow_template_to_dict(
                    self.build_file_to_db_template(
                        file_path="/data/in/orders.csv",
                        file_format="csv",
                        target_connection_name="target_conn",
                        target_datasource_type="postgresql",
                        target_schema="public",
                        target_table="orders_stage",
                        field_transfer_items=[
                            {
                                "readColumn": {"name": "id", "type": 4},
                                "writeColumn": {"name": "id", "type": 4},
                                "deleted": False,
                            },
                            {
                                "readColumn": {"name": "amount", "type": 8},
                                "writeColumn": {"name": "amount", "type": 8},
                                "deleted": False,
                            },
                        ],
                        work_name="文件到数据库示例",
                    )
                ),
                "db_to_file_flow": self.workflow_template_to_dict(
                    self.build_db_to_file_template(
                        source_sql="SELECT id, amount FROM ods_orders",
                        target_path="/data/out/orders.csv",
                        target_file_format="csv",
                        connection_name="source_conn",
                        datasource_type="mysql",
                        work_name="数据库到文件示例",
                    )
                ),
                "file_transfer_flow": self.workflow_template_to_dict(
                    self.build_file_transfer_template(
                        source_path="/data/in/orders.csv",
                        target_path="/data/archive/orders.csv",
                        transfer_mode="COPY",
                        work_name="文件传输示例",
                    )
                ),
            },
            "recommended_flow": [
                "fdl_dev_list_template_node_types",
                "fdl_dev_get_workflow_template_examples",
                "fdl_dev_build_workflow_template_from_dict",
                "fdl_dev_validate_workflow_template",
                "fdl_dev_render_workflow_template",
                "fdl_dev_save_workflow_template",
                "fdl_dev_publish_workflow_template",
            ],
        }

    @staticmethod
    def workflow_template_to_dict(template: WorkflowTemplate) -> dict[str, Any]:
        return {
            "data_flow": {
                "name": template.data_flow.name,
                "nodes": {
                    node_key: {
                        "node_type": node.node_type,
                        "name": node.name,
                        "x": node.x,
                        "y": node.y,
                        "content": node.content,
                        "note": node.note,
                        "execute_logic": node.execute_logic,
                        "disabled": node.disabled,
                    }
                    for node_key, node in template.data_flow.nodes.items()
                },
                "lines": [
                    {
                        "from_node_key": line.from_node_key,
                        "to_node_key": line.to_node_key,
                        "line_condition": line.line_condition,
                        "line_type": line.line_type,
                    }
                    for line in template.data_flow.lines
                ],
                "note": template.data_flow.note,
                "execute_logic": template.data_flow.execute_logic,
                "disabled": template.data_flow.disabled,
            }
        }

    def build_workflow_template(
        self,
        *,
        name: str,
        nodes: dict[str, WorkflowNodeTemplate],
        lines: list[WorkflowLineTemplate] | None = None,
        note: str = "",
        execute_logic: str = "AND",
        disabled: bool = False,
    ) -> WorkflowTemplate:
        template = WorkflowTemplate(
            data_flow=DataFlowTemplate(
                name=name,
                nodes=nodes,
                lines=lines or [],
                note=note,
                execute_logic=execute_logic,
                disabled=disabled,
            )
        )
        self._validate_workflow_template(template)
        return template

    def build_call_task_node_template(
        self,
        *,
        called_work_id: str = "",
        called_work_name: str = "",
        name: str = "调用任务",
        x: int = 286,
        y: int = 480,
    ) -> WorkflowNodeTemplate:
        if not called_work_id and not called_work_name:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="called_work_id or called_work_name cannot both be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="CALL_TASK",
            name=name,
            x=x,
            y=y,
            content={
                "calledWorkId": called_work_id,
                "calledWorkName": called_work_name,
            },
        )

    def build_condition_branch_node_template(
        self,
        *,
        condition: str,
        name: str = "条件分支",
        x: int = 143,
        y: int = 360,
    ) -> WorkflowNodeTemplate:
        if not condition:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="condition cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="CONDITION_BRANCH",
            name=name,
            x=x,
            y=y,
            content={
                "condition": condition,
            },
        )

    def build_param_assign_node_template(
        self,
        *,
        assignments: list[dict[str, Any]],
        name: str = "参数赋值",
        x: int = 286,
        y: int = 360,
    ) -> WorkflowNodeTemplate:
        if not assignments:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="assignments cannot be empty",
                status_code=400,
            )
        return WorkflowNodeTemplate(
            node_type="PARAM_ASSIGN",
            name=name,
            x=x,
            y=y,
            content={
                "assignments": assignments,
            },
        )

    def build_merge_node_template(
        self,
        *,
        name: str = "汇聚",
        x: int = 429,
        y: int = 360,
    ) -> WorkflowNodeTemplate:
        return WorkflowNodeTemplate(
            node_type="MERGE",
            name=name,
            x=x,
            y=y,
            content={},
        )

    def build_sql_to_db_template(self, spec: SQLToDBWorkflowSpec) -> WorkflowTemplate:
        self._validate_sql_to_db_spec(spec)
        return self.build_workflow_template(
            name="数据转换",
            nodes={
                "read": self.build_db_read_node_template(
                    datasource_type=spec.source_datasource_type,
                    connection_name=spec.source_connection_name,
                    sql=spec.source_sql,
                ),
                "write": self.build_db_write_node_template(
                    datasource_type=spec.target_datasource_type,
                    connection_name=spec.target_connection_name,
                    schema=spec.target_schema,
                    table=spec.target_table,
                    field_transfer_items=spec.field_transfer_items,
                    target_database=spec.target_database,
                    target_table_mode=spec.target_table_mode,
                    write_type=spec.write_type,
                    write_node_type=spec.write_node_type,
                    sync_mode=spec.sync_mode,
                    logical_primary_key=spec.logical_primary_key,
                    update_strategy=spec.update_strategy,
                    partition_fields=spec.partition_fields,
                    partition_config=spec.partition_config,
                    distribute_config=spec.distribute_config,
                    write_config=spec.write_config,
                ),
            },
            lines=[WorkflowLineTemplate(from_node_key="read", to_node_key="write")],
        )

    def build_sql_to_python_template(
        self,
        *,
        sql: str,
        python_script: str,
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "SQL转Python",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "sql",
                    self.build_sql_script_node_template(
                        sql=sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                    ),
                ),
                (
                    "python",
                    self.build_python_script_node_template(script=python_script),
                ),
            ],
        )

    def build_sql_python_db_template(
        self,
        *,
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
        write_node_type: str | None = None,
        work_name: str = "SQL-Python-DB",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "sql",
                    self.build_sql_script_node_template(
                        sql=sql,
                        connection_name=source_connection_name,
                        datasource_type=source_datasource_type,
                    ),
                ),
                (
                    "python",
                    self.build_python_script_node_template(script=python_script),
                ),
                (
                    "write",
                    self.build_db_write_node_template(
                        datasource_type=target_datasource_type,
                        connection_name=target_connection_name,
                        schema=target_schema,
                        table=target_table,
                        field_transfer_items=field_transfer_items,
                        target_database=target_database,
                        target_table_mode=target_table_mode,
                        write_type=write_type,
                        write_node_type=write_node_type,
                        sync_mode="OVERWRITE",
                    ),
                ),
            ],
        )

    def build_condition_call_task_template(
        self,
        *,
        condition: str,
        true_called_work_id: str = "",
        true_called_work_name: str = "",
        false_called_work_id: str = "",
        false_called_work_name: str = "",
        work_name: str = "条件调用任务链路",
    ) -> WorkflowTemplate:
        return self.build_workflow_template(
            name=work_name,
            nodes={
                "branch": self.build_condition_branch_node_template(condition=condition),
                "call_true": self.build_call_task_node_template(
                    called_work_id=true_called_work_id,
                    called_work_name=true_called_work_name,
                    name="调用任务(满足条件)",
                ),
                "call_false": self.build_call_task_node_template(
                    called_work_id=false_called_work_id,
                    called_work_name=false_called_work_name,
                    name="调用任务(不满足条件)",
                ),
            },
            lines=[
                WorkflowLineTemplate(
                    from_node_key="branch",
                    to_node_key="call_true",
                    line_condition="ON_TRUE",
                ),
                WorkflowLineTemplate(
                    from_node_key="branch",
                    to_node_key="call_false",
                    line_condition="ON_FALSE",
                ),
            ],
        )

    def build_condition_sql_python_template(
        self,
        *,
        condition: str,
        success_sql: str,
        failure_python_script: str,
        success_connection_name: str = "",
        success_datasource_type: str = "",
        work_name: str = "条件分支链路",
    ) -> WorkflowTemplate:
        return self.build_workflow_template(
            name=work_name,
            nodes={
                "branch": self.build_condition_branch_node_template(condition=condition),
                "sql": self.build_sql_script_node_template(
                    sql=success_sql,
                    connection_name=success_connection_name,
                    datasource_type=success_datasource_type,
                ),
                "python": self.build_python_script_node_template(script=failure_python_script),
            },
            lines=[
                WorkflowLineTemplate(
                    from_node_key="branch",
                    to_node_key="sql",
                    line_condition="ON_TRUE",
                ),
                WorkflowLineTemplate(
                    from_node_key="branch",
                    to_node_key="python",
                    line_condition="ON_FALSE",
                ),
            ],
        )

    def build_condition_param_merge_template(
        self,
        *,
        condition: str,
        true_assignments: list[dict[str, Any]],
        false_assignments: list[dict[str, Any]],
        work_name: str = "条件参数汇聚链路",
    ) -> WorkflowTemplate:
        return self.build_workflow_template(
            name=work_name,
            nodes={
                "branch": self.build_condition_branch_node_template(condition=condition),
                "assign_true": self.build_param_assign_node_template(
                    assignments=true_assignments,
                    name="参数赋值(满足条件)",
                    x=286,
                    y=300,
                ),
                "assign_false": self.build_param_assign_node_template(
                    assignments=false_assignments,
                    name="参数赋值(不满足条件)",
                    x=286,
                    y=420,
                ),
                "merge": self.build_merge_node_template(),
            },
            lines=[
                WorkflowLineTemplate(
                    from_node_key="branch",
                    to_node_key="assign_true",
                    line_condition="ON_TRUE",
                ),
                WorkflowLineTemplate(
                    from_node_key="branch",
                    to_node_key="assign_false",
                    line_condition="ON_FALSE",
                ),
                WorkflowLineTemplate(
                    from_node_key="assign_true",
                    to_node_key="merge",
                ),
                WorkflowLineTemplate(
                    from_node_key="assign_false",
                    to_node_key="merge",
                ),
            ],
        )

    def build_file_to_db_template(
        self,
        *,
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
        write_node_type: str | None = None,
        sync_mode: str = "OVERWRITE",
        logical_primary_key: list[str] | None = None,
        update_strategy: int = 0,
        partition_fields: list[str] | None = None,
        partition_config: dict[str, Any] | None = None,
        distribute_config: dict[str, Any] | None = None,
        write_config: dict[str, Any] | None = None,
        work_name: str = "文件到数据库",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "file",
                    self.build_file_input_node_template(
                        path=file_path,
                        file_format=file_format,
                        delimiter=delimiter,
                        encoding=encoding,
                        has_header=has_header,
                        sheet_name=sheet_name,
                    ),
                ),
                (
                    "write",
                    self.build_db_write_node_template(
                        datasource_type=target_datasource_type,
                        connection_name=target_connection_name,
                        schema=target_schema,
                        table=target_table,
                        field_transfer_items=field_transfer_items,
                        target_database=target_database,
                        target_table_mode=target_table_mode,
                        write_type=write_type,
                        write_node_type=write_node_type,
                        sync_mode=sync_mode,
                        logical_primary_key=logical_primary_key,
                        update_strategy=update_strategy,
                        partition_fields=partition_fields,
                        partition_config=partition_config,
                        distribute_config=distribute_config,
                        write_config=write_config,
                    ),
                ),
            ],
        )

    def build_db_to_file_template(
        self,
        *,
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
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "read",
                    self.build_db_read_node_template(
                        datasource_type=datasource_type,
                        connection_name=connection_name,
                        sql=source_sql,
                    ),
                ),
                (
                    "file",
                    self.build_file_output_node_template(
                        path=target_path,
                        file_format=target_file_format,
                        delimiter=delimiter,
                        encoding=encoding,
                        include_header=include_header,
                        sheet_name=sheet_name,
                        overwrite=overwrite,
                    ),
                ),
            ],
        )

    def build_file_transfer_template(
        self,
        *,
        source_path: str,
        target_path: str,
        transfer_mode: str = "COPY",
        overwrite: bool = True,
        work_name: str = "文件传输链路",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "transfer",
                    self.build_file_transfer_node_template(
                        source_path=source_path,
                        target_path=target_path,
                        transfer_mode=transfer_mode,
                        overwrite=overwrite,
                        x=143,
                        y=120,
                    ),
                )
            ],
        )

    def build_api_to_param_output_template(
        self,
        *,
        api_url: str,
        output_fields: list[str],
        method: str = "GET",
        headers: dict[str, Any] | None = None,
        query: dict[str, Any] | None = None,
        body: Any = None,
        timeout_ms: int = 10000,
        work_name: str = "API转参数输出",
    ) -> WorkflowTemplate:
        outputs = [{"name": field, "sourceField": field} for field in output_fields]
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "api",
                    self.build_api_input_node_template(
                        url=api_url,
                        method=method,
                        headers=headers,
                        query=query,
                        body=body,
                        timeout_ms=timeout_ms,
                    ),
                ),
                (
                    "output",
                    self.build_param_output_node_template(outputs=outputs),
                ),
            ],
        )

    def build_join_template(
        self,
        *,
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
    ) -> WorkflowTemplate:
        return self.build_workflow_template(
            name=work_name,
            nodes={
                "left": self.build_sql_script_node_template(
                    sql=left_sql,
                    connection_name=left_connection_name,
                    datasource_type=left_datasource_type,
                    name="左侧输入SQL",
                    x=0,
                    y=80,
                ),
                "right": self.build_sql_script_node_template(
                    sql=right_sql,
                    connection_name=right_connection_name,
                    datasource_type=right_datasource_type,
                    name="右侧输入SQL",
                    x=0,
                    y=200,
                ),
                "join": self.build_join_node_template(
                    left_keys=left_keys,
                    right_keys=right_keys,
                    join_type=join_type,
                    x=220,
                    y=140,
                ),
            },
            lines=[
                WorkflowLineTemplate(from_node_key="left", to_node_key="join"),
                WorkflowLineTemplate(from_node_key="right", to_node_key="join"),
            ],
        )

    def build_data_compare_template(
        self,
        *,
        left_sql: str,
        right_sql: str,
        compare_keys: list[str],
        include_equal_rows: bool = True,
        left_connection_name: str = "",
        left_datasource_type: str = "",
        right_connection_name: str = "",
        right_datasource_type: str = "",
        work_name: str = "数据比对链路",
    ) -> WorkflowTemplate:
        return self.build_workflow_template(
            name=work_name,
            nodes={
                "left": self.build_sql_script_node_template(
                    sql=left_sql,
                    connection_name=left_connection_name,
                    datasource_type=left_datasource_type,
                    name="主数据SQL",
                    x=0,
                    y=80,
                ),
                "right": self.build_sql_script_node_template(
                    sql=right_sql,
                    connection_name=right_connection_name,
                    datasource_type=right_datasource_type,
                    name="对照数据SQL",
                    x=0,
                    y=200,
                ),
                "compare": self.build_data_compare_node_template(
                    compare_keys=compare_keys,
                    include_equal_rows=include_equal_rows,
                    x=220,
                    y=140,
                ),
            },
            lines=[
                WorkflowLineTemplate(from_node_key="left", to_node_key="compare"),
                WorkflowLineTemplate(from_node_key="right", to_node_key="compare"),
            ],
        )

    def build_union_template(
        self,
        *,
        upstream_sqls: list[str],
        union_mode: str = "ALL",
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "上下合并链路",
    ) -> WorkflowTemplate:
        if len(upstream_sqls) < 2:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="upstream_sqls must contain at least two SQL statements",
                status_code=400,
            )
        node_items: list[tuple[str, WorkflowNodeTemplate]] = []
        lines: list[WorkflowLineTemplate] = []
        for idx, sql in enumerate(upstream_sqls, start=1):
            key = f"source_{idx}"
            node_items.append(
                (
                    key,
                    self.build_sql_script_node_template(
                        sql=sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        name=f"输入SQL{idx}",
                        x=0,
                        y=idx * 120,
                    ),
                )
            )
            lines.append(WorkflowLineTemplate(from_node_key=key, to_node_key="union"))

        return self.build_workflow_template(
            name=work_name,
            nodes={
                **dict(node_items),
                "union": self.build_union_node_template(union_mode=union_mode, x=220, y=200),
            },
            lines=lines,
        )

    def build_unpivot_template(
        self,
        *,
        source_sql: str,
        value_fields: list[str],
        index_fields: list[str] | None = None,
        variable_field_name: str = "metric_name",
        value_field_name: str = "metric_value",
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "列转行链路",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "source",
                    self.build_sql_script_node_template(
                        sql=source_sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        name="源数据SQL",
                    ),
                ),
                (
                    "unpivot",
                    self.build_unpivot_node_template(
                        index_fields=index_fields or [],
                        value_fields=value_fields,
                        variable_field_name=variable_field_name,
                        value_field_name=value_field_name,
                    ),
                ),
            ],
        )

    def build_json_parse_template(
        self,
        *,
        source_sql: str,
        source_field: str,
        target_fields: list[dict[str, Any]],
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "JSON解析链路",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "source",
                    self.build_sql_script_node_template(
                        sql=source_sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        name="源数据SQL",
                    ),
                ),
                (
                    "json_parse",
                    self.build_json_parse_node_template(
                        source_field=source_field,
                        target_fields=target_fields,
                    ),
                ),
            ],
        )

    def build_row_filter_template(
        self,
        *,
        source_sql: str,
        condition: str,
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "行过滤链路",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "source",
                    self.build_sql_script_node_template(
                        sql=source_sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        name="源数据SQL",
                    ),
                ),
                (
                    "filter",
                    self.build_row_filter_node_template(condition=condition),
                ),
            ],
        )

    def build_field_select_template(
        self,
        *,
        source_sql: str,
        selected_fields: list[dict[str, Any]],
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "字段选择链路",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "source",
                    self.build_sql_script_node_template(
                        sql=source_sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        name="源数据SQL",
                    ),
                ),
                (
                    "select",
                    self.build_field_select_node_template(selected_fields=selected_fields),
                ),
            ],
        )

    def build_sort_template(
        self,
        *,
        source_sql: str,
        sort_fields: list[dict[str, Any]],
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "排序链路",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "source",
                    self.build_sql_script_node_template(
                        sql=source_sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        name="源数据SQL",
                    ),
                ),
                (
                    "sort",
                    self.build_sort_node_template(sort_fields=sort_fields),
                ),
            ],
        )

    def build_aggregate_template(
        self,
        *,
        source_sql: str,
        aggregations: list[dict[str, Any]],
        group_fields: list[str] | None = None,
        connection_name: str = "",
        datasource_type: str = "",
        work_name: str = "聚合链路",
    ) -> WorkflowTemplate:
        return self.build_linear_workflow_template(
            name=work_name,
            node_items=[
                (
                    "source",
                    self.build_sql_script_node_template(
                        sql=source_sql,
                        connection_name=connection_name,
                        datasource_type=datasource_type,
                        name="源数据SQL",
                    ),
                ),
                (
                    "aggregate",
                    self.build_aggregate_node_template(
                        group_fields=group_fields,
                        aggregations=aggregations,
                    ),
                ),
            ],
        )

    def build_db_to_db_template(self, spec: DBToDBWorkflowSpec) -> WorkflowTemplate:
        return self.build_sql_to_db_template(spec)

    def build_workflow_from_template(
        self,
        template: WorkflowTemplate,
        *,
        work_name: str,
        work_id: str | None = None,
    ) -> dict[str, Any]:
        if not work_name:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="work_name cannot be empty",
                status_code=400,
            )

        generated_work_id = work_id or self._new_id()
        data_flow_id = self._new_id()
        node_ids = {node_key: self._new_id() for node_key in template.data_flow.nodes}

        rendered_nodes = []
        for node_key, node_template in template.data_flow.nodes.items():
            rendered_nodes.append(
                {
                    "x": node_template.x,
                    "y": node_template.y,
                    "nodeType": node_template.node_type,
                    "nodeContent": {
                        **node_template.content,
                        "id": node_ids[node_key],
                        "name": node_template.name,
                        "note": node_template.note,
                        "executeLogic": node_template.execute_logic,
                        "disabled": node_template.disabled,
                    },
                    "compareId": self._new_id(),
                }
            )

        rendered_lines = [
            {
                "lineType": line.line_type,
                "value": {
                    "from": node_ids[line.from_node_key],
                    "to": node_ids[line.to_node_key],
                    "lineCondition": line.line_condition,
                },
            }
            for line in template.data_flow.lines
        ]

        return {
            "workId": generated_work_id,
            "checkState": "SUCCESS",
            "workBook": {
                "id": generated_work_id,
                "name": work_name,
                "params": [],
                "notes": [],
                "graph": {
                    "offsetX": 0,
                    "offsetY": 0,
                    "edgeType": "polyline",
                    "scale": 100,
                    "allowAdsorption": True,
                    "showRuntimeStatus": True,
                },
                "nodes": [
                    {
                        "compareId": self._new_id(),
                        "type": "DATA_FLOW",
                        "value": {
                            "graph": {
                                "edgeType": "polyline",
                                "scale": 100,
                                "allowAdsorption": True,
                                "showRuntimeStatus": True,
                            },
                            "nodes": rendered_nodes,
                            "lines": rendered_lines,
                            "notes": [],
                            "id": data_flow_id,
                            "name": template.data_flow.name,
                            "note": template.data_flow.note,
                            "executeLogic": template.data_flow.execute_logic,
                            "disabled": template.data_flow.disabled,
                        },
                        "defaultParams": None,
                        "x": -168,
                        "y": 224,
                    }
                ],
                "lines": [],
            },
            "externalJsonStrings": {},
        }

    def build_publish_payload(
        self,
        save_payload: dict[str, Any],
        *,
        describe: str = "",
        sub_work_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        if not isinstance(save_payload, dict) or not save_payload:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="save_payload cannot be empty",
                status_code=400,
            )
        return {
            "dataDevWork": save_payload,
            "subWorkIds": sub_work_ids or [],
            "describe": describe,
        }

    def build_field_debug_payload(
        self,
        save_payload: dict[str, Any],
        *,
        chosen_node_id: str | None = None,
        preview_type: str = "",
    ) -> dict[str, Any]:
        data_flow = self._get_data_flow_node(save_payload)
        target_node = self._get_inner_node(data_flow, "DB_WRITE")
        return {
            "node": data_flow,
            "paramEntity": {
                "workParams": [
                    {
                        "name": "workname",
                        "value": save_payload["workBook"]["name"],
                        "valueType": "STRING",
                    }
                ],
                "nodeParams": [],
            },
            "previewOptions": {
                "chosenNodeId": chosen_node_id or target_node["nodeContent"]["id"],
                "previewType": preview_type,
            },
        }

    def build_partition_payload(self, save_payload: dict[str, Any]) -> dict[str, Any]:
        target_node = self._get_inner_node(self._get_data_flow_node(save_payload), "DB_WRITE")
        node_content = target_node["nodeContent"]
        return {
            "connectionName": node_content["toConnectionName"],
            "schemaName": node_content.get("toSchema", ""),
            "tableName": node_content["toTable"],
        }

    async def prepare_db_to_db_workflow(
        self,
        *,
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
        write_node_type: str | None = None,
        sync_mode: str = "OVERWRITE",
        logical_primary_key: list[str] | None = None,
        update_strategy: int = 0,
        partition_fields: list[str] | None = None,
        partition_config: dict[str, Any] | None = None,
        distribute_config: dict[str, Any] | None = None,
        write_config: dict[str, Any] | None = None,
        work_id: str | None = None,
    ) -> tuple[dict[str, Any], int, str]:
        save_payload = self.build_db_to_db_workflow(
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
            write_node_type=write_node_type,
            sync_mode=sync_mode,
            logical_primary_key=logical_primary_key,
            update_strategy=update_strategy,
            partition_fields=partition_fields,
            partition_config=partition_config,
            distribute_config=distribute_config,
            write_config=write_config,
            work_id=work_id,
        )
        field_payload = self.build_field_debug_payload(save_payload)
        partition_payload = self.build_partition_payload(save_payload)
        target_fields, _, _ = await self.get_target_fields(field_payload)
        refreshed_fields, _, _ = await self.refresh_fields(field_payload)
        partition_config, status_code, endpoint = await self.get_partition_config(partition_payload)
        return {
            "save_payload": save_payload,
            "field_payload": field_payload,
            "partition_payload": partition_payload,
            "target_fields": target_fields,
            "refreshed_fields": refreshed_fields,
            "partition_config": partition_config,
        }, status_code, endpoint

    async def save_db_to_db_workflow(
        self,
        *,
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
        write_node_type: str | None = None,
        sync_mode: str = "OVERWRITE",
        logical_primary_key: list[str] | None = None,
        update_strategy: int = 0,
        partition_fields: list[str] | None = None,
        partition_config: dict[str, Any] | None = None,
        distribute_config: dict[str, Any] | None = None,
        write_config: dict[str, Any] | None = None,
        work_id: str | None = None,
    ) -> tuple[Any, int, str]:
        payload = self.build_db_to_db_workflow(
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
            write_node_type=write_node_type,
            sync_mode=sync_mode,
            logical_primary_key=logical_primary_key,
            update_strategy=update_strategy,
            partition_fields=partition_fields,
            partition_config=partition_config,
            distribute_config=distribute_config,
            write_config=write_config,
            work_id=work_id,
        )
        return await self.save_work(payload)

    async def publish_db_to_db_workflow(
        self,
        *,
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
        write_node_type: str | None = None,
        sync_mode: str = "OVERWRITE",
        logical_primary_key: list[str] | None = None,
        update_strategy: int = 0,
        partition_fields: list[str] | None = None,
        partition_config: dict[str, Any] | None = None,
        distribute_config: dict[str, Any] | None = None,
        write_config: dict[str, Any] | None = None,
        work_id: str | None = None,
    ) -> tuple[dict[str, Any], int, str]:
        save_payload = self.build_db_to_db_workflow(
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
            write_node_type=write_node_type,
            sync_mode=sync_mode,
            logical_primary_key=logical_primary_key,
            update_strategy=update_strategy,
            partition_fields=partition_fields,
            partition_config=partition_config,
            distribute_config=distribute_config,
            write_config=write_config,
            work_id=work_id,
        )
        save_result, _, _ = await self.save_work(save_payload)
        publish_payload = self.build_publish_payload(
            save_payload,
            describe=describe,
            sub_work_ids=sub_work_ids,
        )
        check_result, _, _ = await self.publish_work_check(save_payload)
        publish_result, status_code, endpoint = await self.publish_work(publish_payload)
        return {
            "save_payload": save_payload,
            "publish_payload": publish_payload,
            "save_result": save_result,
            "publish_check_result": check_result,
            "publish_result": publish_result,
        }, status_code, endpoint

    async def save_workflow_template(
        self,
        *,
        template: dict[str, Any],
        work_name: str,
        work_id: str | None = None,
    ) -> tuple[Any, int, str]:
        save_payload = self.build_workflow_from_template(
            self.workflow_template_from_dict(template),
            work_name=work_name,
            work_id=work_id,
        )
        return await self.save_work(save_payload)

    def render_workflow_templates_batch(
        self,
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not items:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="items cannot be empty",
                status_code=400,
            )
        rendered_items = []
        for item in items:
            template = item.get("template")
            work_name = item.get("work_name", "")
            work_id = item.get("work_id") or None
            rendered_items.append(
                {
                    "work_name": work_name,
                    "work_id": work_id,
                    "save_payload": self.build_workflow_from_template(
                        self.workflow_template_from_dict(template),
                        work_name=work_name,
                        work_id=work_id,
                    ),
                }
            )
        return rendered_items

    async def save_workflow_templates_batch(
        self,
        items: list[dict[str, Any]],
    ) -> tuple[list[dict[str, Any]], int, str]:
        rendered_items = self.render_workflow_templates_batch(items)
        results: list[dict[str, Any]] = []
        final_status_code = 200
        final_endpoint = "/webroot/decision/fdl/dev/work/save"
        for item in rendered_items:
            data, status_code, endpoint = await self.save_work(item["save_payload"])
            final_status_code = status_code
            final_endpoint = endpoint
            results.append(
                {
                    "work_name": item["work_name"],
                    "work_id": item["save_payload"]["workId"],
                    "save_payload": item["save_payload"],
                    "result": data,
                    "status_code": status_code,
                    "endpoint": endpoint,
                }
            )
        return results, final_status_code, final_endpoint

    async def publish_workflow_template(
        self,
        *,
        template: dict[str, Any],
        work_name: str,
        work_id: str | None = None,
        describe: str = "",
        sub_work_ids: list[str] | None = None,
    ) -> tuple[dict[str, Any], int, str]:
        save_payload = self.build_workflow_from_template(
            self.workflow_template_from_dict(template),
            work_name=work_name,
            work_id=work_id,
        )
        save_result, _, _ = await self.save_work(save_payload)
        publish_payload = self.build_publish_payload(
            save_payload,
            describe=describe,
            sub_work_ids=sub_work_ids,
        )
        check_result, _, _ = await self.publish_work_check(save_payload)
        publish_result, status_code, endpoint = await self.publish_work(publish_payload)
        return {
            "save_payload": save_payload,
            "publish_payload": publish_payload,
            "save_result": save_result,
            "publish_check_result": check_result,
            "publish_result": publish_result,
        }, status_code, endpoint

    async def save_work(self, payload: dict[str, Any] | list[Any] | str) -> tuple[Any, int, str]:
        if payload is None or payload == "" or payload == {} or payload == []:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="payload cannot be empty",
                status_code=400,
            )
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/work/save",
            body=payload,
            encrypted=True,
        )

    async def publish_work_check(self, payload: dict[str, Any] | list[Any] | str) -> tuple[Any, int, str]:
        if payload is None or payload == "" or payload == {} or payload == []:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="payload cannot be empty",
                status_code=400,
            )
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/work/publish/check",
            body=payload,
            encrypted=True,
        )

    async def publish_work(self, payload: dict[str, Any] | list[Any] | str) -> tuple[Any, int, str]:
        if payload is None or payload == "" or payload == {} or payload == []:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="payload cannot be empty",
                status_code=400,
            )
        return await self.client.request_fdl_dev(
            "POST",
            "/webroot/decision/fdl/dev/work/publish",
            body=payload,
            encrypted=True,
        )

    @staticmethod
    def workflow_template_from_dict(payload: dict[str, Any]) -> WorkflowTemplate:
        try:
            data_flow_payload = payload["data_flow"]
            nodes_payload = data_flow_payload["nodes"]
            lines_payload = data_flow_payload.get("lines", [])
        except (KeyError, TypeError) as exc:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="template payload is invalid",
                status_code=400,
            ) from exc

        template = WorkflowTemplate(
            data_flow=DataFlowTemplate(
                name=data_flow_payload["name"],
                nodes={
                    node_key: WorkflowNodeTemplate(
                        node_type=node_payload["node_type"],
                        name=node_payload["name"],
                        x=node_payload["x"],
                        y=node_payload["y"],
                        content=node_payload["content"],
                        note=node_payload.get("note", ""),
                        execute_logic=node_payload.get("execute_logic", "AND"),
                        disabled=node_payload.get("disabled", False),
                    )
                    for node_key, node_payload in nodes_payload.items()
                },
                lines=[
                    WorkflowLineTemplate(
                        from_node_key=line_payload["from_node_key"],
                        to_node_key=line_payload["to_node_key"],
                        line_condition=line_payload.get("line_condition", "ON_SUCCESS"),
                        line_type=line_payload.get("line_type", "DEFAULT"),
                    )
                    for line_payload in lines_payload
                ],
                note=data_flow_payload.get("note", ""),
                execute_logic=data_flow_payload.get("execute_logic", "AND"),
                disabled=data_flow_payload.get("disabled", False),
            )
        )
        DevService._validate_workflow_template(template)
        return template

    @staticmethod
    def _validate_workflow_template(template: WorkflowTemplate) -> None:
        if not template.data_flow.name:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="workflow template name cannot be empty",
                status_code=400,
            )
        if not template.data_flow.nodes:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="workflow template nodes cannot be empty",
                status_code=400,
            )
        outgoing_lines_by_node: dict[str, list[WorkflowLineTemplate]] = {}
        for line in template.data_flow.lines:
            if line.from_node_key not in template.data_flow.nodes:
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message=f"line source node {line.from_node_key} does not exist",
                    status_code=400,
                )
            if line.to_node_key not in template.data_flow.nodes:
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message=f"line target node {line.to_node_key} does not exist",
                    status_code=400,
                )
            outgoing_lines_by_node.setdefault(line.from_node_key, []).append(line)

        for node_key, node in template.data_flow.nodes.items():
            outgoing_lines = outgoing_lines_by_node.get(node_key, [])
            if node.node_type == "CONDITION_BRANCH":
                conditions = {line.line_condition for line in outgoing_lines}
                if conditions != {"ON_TRUE", "ON_FALSE"}:
                    raise FDLError(
                        code="FDL_TASK_INVALID_INPUT",
                        message="CONDITION_BRANCH nodes must have ON_TRUE and ON_FALSE outgoing lines",
                        status_code=400,
                    )
            if node.node_type == "PARAM_ASSIGN" and not node.content.get("assignments"):
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message="PARAM_ASSIGN nodes must define assignments",
                    status_code=400,
                )
            if node.node_type == "API_INPUT":
                request_payload = node.content.get("request")
                if not isinstance(request_payload, dict) or not request_payload.get("url"):
                    raise FDLError(
                        code="FDL_TASK_INVALID_INPUT",
                        message="API_INPUT nodes must define request.url",
                        status_code=400,
                    )
            if node.node_type == "PARAM_OUTPUT" and not node.content.get("outputs"):
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message="PARAM_OUTPUT nodes must define outputs",
                    status_code=400,
                )
            if node.node_type == "JSON_PARSE":
                if not node.content.get("sourceField") or not node.content.get("targetFields"):
                    raise FDLError(
                        code="FDL_TASK_INVALID_INPUT",
                        message="JSON_PARSE nodes must define sourceField and targetFields",
                        status_code=400,
                    )
            if node.node_type == "ROW_FILTER" and not node.content.get("condition"):
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message="ROW_FILTER nodes must define condition",
                    status_code=400,
                )
            if node.node_type == "FIELD_SELECT" and not node.content.get("selectedFields"):
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message="FIELD_SELECT nodes must define selectedFields",
                    status_code=400,
                )
            if node.node_type == "SORT" and not node.content.get("sortFields"):
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message="SORT nodes must define sortFields",
                    status_code=400,
                )
            if node.node_type == "AGGREGATE" and not node.content.get("aggregations"):
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message="AGGREGATE nodes must define aggregations",
                    status_code=400,
                )
            if node.node_type == "MERGE" and len(outgoing_lines) > 1:
                raise FDLError(
                    code="FDL_TASK_INVALID_INPUT",
                    message="MERGE nodes can have at most one outgoing line",
                    status_code=400,
                )

    @staticmethod
    def _validate_sql_to_db_spec(spec: SQLToDBWorkflowSpec) -> None:
        if not spec.work_name:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="work_name cannot be empty",
                status_code=400,
            )
        if not spec.source_connection_name:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="source_connection_name cannot be empty",
                status_code=400,
            )
        if not spec.source_sql:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="source_sql cannot be empty",
                status_code=400,
            )
        if not spec.target_connection_name:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="target_connection_name cannot be empty",
                status_code=400,
            )
        if not spec.target_table:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="target_table cannot be empty",
                status_code=400,
            )
        if not spec.field_transfer_items:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="field_transfer_items cannot be empty",
                status_code=400,
            )

    @staticmethod
    def _validate_db_to_db_spec(spec: DBToDBWorkflowSpec) -> None:
        DevService._validate_sql_to_db_spec(spec)

    @staticmethod
    def _get_data_flow_node(save_payload: dict[str, Any]) -> dict[str, Any]:
        try:
            node = save_payload["workBook"]["nodes"][0]
        except (KeyError, IndexError, TypeError) as exc:
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="save_payload does not contain a usable DATA_FLOW node",
                status_code=400,
            ) from exc
        if node.get("type") != "DATA_FLOW":
            raise FDLError(
                code="FDL_TASK_INVALID_INPUT",
                message="save_payload first node is not DATA_FLOW",
                status_code=400,
            )
        return node

    @staticmethod
    def _get_inner_node(data_flow_node: dict[str, Any], node_type: str) -> dict[str, Any]:
        for node in data_flow_node.get("value", {}).get("nodes", []):
            if node.get("nodeType") == node_type:
                return node
        raise FDLError(
            code="FDL_TASK_INVALID_INPUT",
            message=f"DATA_FLOW does not contain node type {node_type}",
            status_code=400,
        )

    @staticmethod
    def _new_id() -> str:
        return str(uuid.uuid4())
