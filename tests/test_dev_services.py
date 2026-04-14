import httpx
import pytest

from fdl_mcp.auth import AppCodeAuth
from fdl_mcp.client import FDLClient
from fdl_mcp.dev_services import (
    DBToDBWorkflowSpec,
    DevService,
    SQLToDBWorkflowSpec,
    WorkflowLineTemplate,
    WorkflowNodeTemplate,
    WorkflowTemplate,
)
from fdl_mcp.endpoint_resolver import EndpointResolver
from fdl_mcp.errors import FDLError


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("method_name", "args", "expected_path", "expected_encrypt"),
    [
        ("get_connection_info", ("demo_conn",), "/webroot/decision/fdl/dev/conn/info", "plaintext"),
        ("list_connection_schemas", ("demo_conn",), "/webroot/decision/fdl/dev/conn/datasource/schemas", "plaintext"),
        (
            "list_table_views",
            ("demo_conn", "demo_db", "public"),
            "/webroot/decision/fdl/dev/datasource/schema/tableViews",
            "plaintext",
        ),
        ("get_global_params", (), "/webroot/decision/fdl/dev/param/global/query", "plaintext"),
        (
            "get_development_instance_info",
            ("work-1",),
            "/webroot/decision/fdl/dev/instance/work-1/development/info/get",
            "plaintext",
        ),
        ("list_work_versions", ("work-1",), "/webroot/decision/fdl/dev/work/work-1/versions", "plaintext"),
        (
            "get_published_work_info",
            ("work-1", "manual"),
            "/webroot/decision/fdl/dev/work/info/work-1/published",
            "plaintext",
        ),
        (
            "get_catalog_entity_info",
            ("work-1",),
            "/webroot/decision/fdl/dev/catalog/entity/info",
            "plaintext",
        ),
        (
            "get_work_development_info",
            ("work-1",),
            "/webroot/decision/fdl/dev/work/info/work-1/development",
            "plaintext",
        ),
        ("list_functions", (), "/webroot/decision/fdl/dev/function/list", "plaintext"),
        (
            "get_downstream",
            ("work-1",),
            "/webroot/decision/fdl/plan/event/work-1/downstream/get",
            "plaintext",
        ),
        (
            "get_published_instance_info",
            ("work-1",),
            "/webroot/decision/fdl/dev/instance/work-1/published/info/get",
            "plaintext",
        ),
        (
            "preview_datasource",
            ({"node": "demo"},),
            "/webroot/decision/fdl/dev/datasource/preview",
            "encrypted",
        ),
        (
            "get_source_fields",
            ({"node": "demo"},),
            "/webroot/decision/fdl/dev/datasource/field/source",
            "encrypted",
        ),
        (
            "get_target_fields",
            ({"node": "demo"},),
            "/webroot/decision/fdl/dev/datasource/field/target",
            "encrypted",
        ),
        (
            "refresh_fields",
            ({"node": "demo"},),
            "/webroot/decision/fdl/dev/datasource/field/refresh",
            "encrypted",
        ),
        (
            "get_field_modifies",
            ({"node": "demo"},),
            "/webroot/decision/fdl/dev/datasource/field/modifies",
            "encrypted",
        ),
        (
            "get_partition_config",
            ({"connectionName": "dst", "tableName": "demo"},),
            "/webroot/decision/fdl/dev/conn/table/conf/partition/get",
            "encrypted",
        ),
    ],
)
async def test_confirmed_dev_endpoints_use_expected_paths(
    method_name: str,
    args: tuple[object, ...],
    expected_path: str,
    expected_encrypt: str,
) -> None:
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["query"] = dict(request.url.params)
        captured["encrypt"] = request.headers["fdl-encrypt"]
        return httpx.Response(200, json={"ok": True})

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            transport=httpx.MockTransport(handler),
        )
    )

    method = getattr(service, method_name)
    data, status, endpoint = await method(*args)

    assert data == {"ok": True}
    assert status == 200
    assert endpoint == expected_path
    assert captured["path"] == expected_path
    assert captured["encrypt"] == expected_encrypt

    if method_name == "get_connection_info":
        assert captured["query"] == {"connectionName": "demo_conn"}
    elif method_name == "list_connection_schemas":
        assert captured["query"] == {"connectionName": "demo_conn"}
    elif method_name == "list_table_views":
        assert captured["query"] == {"connection": "demo_conn", "database": "demo_db", "schema": "public"}
    elif method_name == "get_published_work_info":
        assert captured["query"] == {"source": "manual"}
    elif method_name == "get_catalog_entity_info":
        assert captured["query"] == {"workId": "work-1"}
    else:
        assert captured["query"] == {}


@pytest.mark.asyncio
async def test_list_connections_uses_expected_endpoint() -> None:
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["encrypt"] = request.headers["fdl-encrypt"]
        return httpx.Response(200, json={"data": []})

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.list_connections("mysql")
    assert data == {"data": []}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/conn/fr/get/mysql"
    assert captured == {
        "path": "/webroot/decision/fdl/dev/conn/fr/get/mysql",
        "encrypt": "plaintext",
    }


@pytest.mark.asyncio
async def test_publish_work_encrypts_plaintext_payload() -> None:
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["encrypt"] = request.headers["fdl-encrypt"]
        captured["body"] = request.content.decode("utf-8")
        return httpx.Response(200, json={"code": 200})

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            encrypt_mode="aes",
            encrypt_key="1ED6F5BA8CFD75F8",
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.publish_work({"name": "demo"})
    assert data == {"code": 200}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/publish"
    assert captured == {
        "path": "/webroot/decision/fdl/dev/work/publish",
        "encrypt": "encrypted",
        "body": "PJIwE/gRfS6vGyZuWmg+NA==",
    }


def test_build_db_read_node_template_returns_reusable_read_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_db_read_node_template(
        datasource_type="mysql",
        connection_name="finedb",
        sql="SELECT 1",
        x=12,
        y=34,
    )

    assert node.node_type == "DB_READ"
    assert node.name == "DB表输入"
    assert node.x == 12
    assert node.y == 34
    assert node.content["fromDatasourceType"] == "mysql"
    assert node.content["fromConnectionName"] == "finedb"
    assert node.content["dataBaseConfig"] == {"type": "SQL", "sql": "SELECT 1"}


def test_build_linear_workflow_template_links_nodes_in_order() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_linear_workflow_template(
        name="线性链路",
        node_items=[
            (
                "sql",
                service.build_sql_script_node_template(sql="SELECT 1"),
            ),
            (
                "python",
                service.build_python_script_node_template(script="print('ok')"),
            ),
            (
                "write",
                service.build_db_write_node_template(
                    datasource_type="postgresql",
                    connection_name="dst",
                    schema="public",
                    table="demo_table",
                    field_transfer_items=[
                        {
                            "readColumn": {"name": "id", "type": 4},
                            "writeColumn": {"name": "id", "type": 4},
                            "deleted": False,
                        }
                    ],
                ),
            ),
        ],
    )

    assert list(template.data_flow.nodes) == ["sql", "python", "write"]
    assert len(template.data_flow.lines) == 2
    assert template.data_flow.lines[0].from_node_key == "sql"
    assert template.data_flow.lines[0].to_node_key == "python"
    assert template.data_flow.lines[1].from_node_key == "python"
    assert template.data_flow.lines[1].to_node_key == "write"


def test_list_supported_template_node_types_exposes_agent_schema() -> None:
    schema = DevService.list_supported_template_node_types()

    assert schema["line_conditions"] == ["ON_SUCCESS", "ON_TRUE", "ON_FALSE"]
    assert schema["line_types"] == ["DEFAULT"]
    assert {item["node_type"] for item in schema["node_types"]} == {
        "DB_READ",
        "API_INPUT",
        "FILE_INPUT",
        "FILE_OUTPUT",
        "FILE_TRANSFER",
        "DB_WRITE",
        "SQL_SCRIPT",
        "PYTHON_SCRIPT",
        "CONDITION_BRANCH",
        "PARAM_ASSIGN",
        "PARAM_OUTPUT",
        "JOIN",
        "DATA_COMPARE",
        "UNION",
        "UNPIVOT",
        "JSON_PARSE",
        "ROW_FILTER",
        "FIELD_SELECT",
        "SORT",
        "AGGREGATE",
        "MERGE",
        "CALL_TASK",
    }
    branch_node = next(item for item in schema["node_types"] if item["node_type"] == "CONDITION_BRANCH")
    assert branch_node["required_content_keys"] == ["condition"]
    assert branch_node["line_conditions"] == ["ON_TRUE", "ON_FALSE"]


def test_list_workflow_template_examples_returns_reusable_examples() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    examples = service.list_workflow_template_examples()

    assert set(examples["examples"]) == {
        "sql_to_python",
        "sql_python_db",
        "condition_call_task",
        "condition_param_merge",
        "api_to_param_output",
        "join_flow",
        "data_compare_flow",
        "union_flow",
        "unpivot_flow",
        "json_parse_flow",
        "row_filter_flow",
        "field_select_flow",
        "sort_flow",
        "aggregate_flow",
        "file_to_db_flow",
        "db_to_file_flow",
        "file_transfer_flow",
    }
    assert examples["examples"]["sql_to_python"]["data_flow"]["nodes"]["sql"]["node_type"] == "SQL_SCRIPT"
    assert examples["examples"]["condition_call_task"]["data_flow"]["nodes"]["branch"]["node_type"] == "CONDITION_BRANCH"
    assert examples["recommended_flow"][-1] == "fdl_dev_publish_workflow_template"


def test_build_workflow_template_from_dict_builds_template() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_workflow_template_from_dict(
        name="dict-template",
        nodes={
            "sql": {
                "node_type": "SQL_SCRIPT",
                "name": "SQL脚本",
                "x": 0,
                "y": 0,
                "content": {
                    "sql": "SELECT 1",
                    "connectionName": "",
                    "datasourceType": "",
                },
            },
            "python": {
                "node_type": "PYTHON_SCRIPT",
                "name": "Python脚本",
                "x": 100,
                "y": 0,
                "content": {
                    "script": "print('ok')",
                    "runtime": "python",
                },
            },
        },
        lines=[
            {
                "from_node_key": "sql",
                "to_node_key": "python",
            }
        ],
    )

    assert template.data_flow.name == "dict-template"
    assert template.data_flow.nodes["sql"].node_type == "SQL_SCRIPT"
    assert template.data_flow.lines[0].to_node_key == "python"


def test_build_api_input_node_template_returns_reusable_api_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_api_input_node_template(
        url="https://api.example.com/orders",
        method="post",
        headers={"Authorization": "Bearer demo"},
        query={"page": 1},
        body={"status": "ready"},
        timeout_ms=8000,
        response_mapping=[{"source": "$.data", "target": "rows"}],
        x=22,
        y=44,
    )

    assert node.node_type == "API_INPUT"
    assert node.name == "API输入"
    assert node.x == 22
    assert node.y == 44
    assert node.content["request"]["method"] == "POST"
    assert node.content["request"]["url"] == "https://api.example.com/orders"
    assert node.content["request"]["headers"]["Authorization"] == "Bearer demo"
    assert node.content["request"]["query"] == {"page": 1}
    assert node.content["request"]["body"] == {"status": "ready"}
    assert node.content["request"]["timeoutMs"] == 8000
    assert node.content["responseMapping"] == [{"source": "$.data", "target": "rows"}]


def test_build_param_output_node_template_returns_reusable_output_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_param_output_node_template(
        outputs=[{"name": "order_id", "sourceField": "id"}],
        x=300,
        y=55,
    )

    assert node.node_type == "PARAM_OUTPUT"
    assert node.name == "参数输出"
    assert node.x == 300
    assert node.y == 55
    assert node.content == {"outputs": [{"name": "order_id", "sourceField": "id"}]}


def test_build_api_to_param_output_template_returns_two_stage_template() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_api_to_param_output_template(
        api_url="https://api.example.com/orders",
        output_fields=["order_id", "status"],
    )

    assert template.data_flow.name == "API转参数输出"
    assert list(template.data_flow.nodes) == ["api", "output"]
    assert template.data_flow.nodes["api"].node_type == "API_INPUT"
    assert template.data_flow.nodes["output"].node_type == "PARAM_OUTPUT"
    assert template.data_flow.nodes["output"].content["outputs"] == [
        {"name": "order_id", "sourceField": "order_id"},
        {"name": "status", "sourceField": "status"},
    ]


def test_build_api_to_param_output_template_rejects_empty_output_fields() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError, match="outputs cannot be empty"):
        service.build_api_to_param_output_template(
            api_url="https://api.example.com/orders",
            output_fields=[],
        )


def test_build_join_template_creates_two_input_join_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_join_template(
        left_sql="SELECT id, amount FROM orders",
        right_sql="SELECT id, level FROM users",
        left_keys=["id"],
        right_keys=["id"],
        join_type="left",
    )

    assert template.data_flow.name == "数据关联链路"
    assert list(template.data_flow.nodes) == ["left", "right", "join"]
    assert template.data_flow.nodes["join"].node_type == "JOIN"
    assert template.data_flow.nodes["join"].content == {
        "joinType": "LEFT",
        "leftKeys": ["id"],
        "rightKeys": ["id"],
    }
    assert len(template.data_flow.lines) == 2
    assert template.data_flow.lines[0].to_node_key == "join"
    assert template.data_flow.lines[1].to_node_key == "join"


def test_build_data_compare_template_creates_two_input_compare_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_data_compare_template(
        left_sql="SELECT id, dt FROM ods_orders",
        right_sql="SELECT id, dt FROM dwd_orders",
        compare_keys=["id"],
        include_equal_rows=False,
    )

    assert template.data_flow.name == "数据比对链路"
    assert list(template.data_flow.nodes) == ["left", "right", "compare"]
    assert template.data_flow.nodes["compare"].node_type == "DATA_COMPARE"
    assert template.data_flow.nodes["compare"].content == {
        "compareKeys": ["id"],
        "includeEqualRows": False,
    }
    assert len(template.data_flow.lines) == 2


def test_build_union_template_rejects_less_than_two_sources() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError, match="at least two SQL statements"):
        service.build_union_template(upstream_sqls=["SELECT 1"])


def test_build_union_template_creates_multi_input_union_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_union_template(
        upstream_sqls=["SELECT id FROM a", "SELECT id FROM b", "SELECT id FROM c"],
        union_mode="distinct",
    )

    assert template.data_flow.name == "上下合并链路"
    assert list(template.data_flow.nodes) == ["source_1", "source_2", "source_3", "union"]
    assert template.data_flow.nodes["union"].node_type == "UNION"
    assert template.data_flow.nodes["union"].content == {"unionMode": "DISTINCT"}
    assert len(template.data_flow.lines) == 3
    assert all(line.to_node_key == "union" for line in template.data_flow.lines)


def test_build_unpivot_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_unpivot_template(
        source_sql="SELECT id, pv, uv FROM ads_daily_metrics",
        index_fields=["id"],
        value_fields=["pv", "uv"],
        variable_field_name="metric",
        value_field_name="value",
    )

    assert template.data_flow.name == "列转行链路"
    assert list(template.data_flow.nodes) == ["source", "unpivot"]
    assert template.data_flow.nodes["unpivot"].node_type == "UNPIVOT"
    assert template.data_flow.nodes["unpivot"].content == {
        "indexFields": ["id"],
        "valueFields": ["pv", "uv"],
        "variableFieldName": "metric",
        "valueFieldName": "value",
    }


def test_build_json_parse_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    target_fields = [
        {"name": "province", "jsonPath": "$.address.province"},
        {"name": "city", "jsonPath": "$.address.city"},
    ]
    template = service.build_json_parse_template(
        source_sql="SELECT id, ext_json FROM ods_orders",
        source_field="ext_json",
        target_fields=target_fields,
    )

    assert template.data_flow.name == "JSON解析链路"
    assert list(template.data_flow.nodes) == ["source", "json_parse"]
    assert template.data_flow.nodes["json_parse"].node_type == "JSON_PARSE"
    assert template.data_flow.nodes["json_parse"].content == {
        "sourceField": "ext_json",
        "targetFields": target_fields,
    }


def test_validate_workflow_template_rejects_api_input_without_url() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError, match="API_INPUT nodes must define request.url"):
        service.build_workflow_template_from_dict(
            name="invalid-api-template",
            nodes={
                "api": {
                    "node_type": "API_INPUT",
                    "name": "API输入",
                    "x": 0,
                    "y": 0,
                    "content": {
                        "request": {"method": "GET", "url": ""},
                        "responseMapping": [],
                    },
                }
            },
        )


def test_validate_workflow_template_rejects_param_output_without_outputs() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError, match="PARAM_OUTPUT nodes must define outputs"):
        service.build_workflow_template_from_dict(
            name="invalid-output-template",
            nodes={
                "output": {
                    "node_type": "PARAM_OUTPUT",
                    "name": "参数输出",
                    "x": 0,
                    "y": 0,
                    "content": {"outputs": []},
                }
            },
        )


def test_build_call_task_node_template_returns_call_task_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_call_task_node_template(called_work_name="daily_sync", x=286, y=480)

    assert node.node_type == "CALL_TASK"
    assert node.name == "调用任务"
    assert node.content == {
        "calledWorkId": "",
        "calledWorkName": "daily_sync",
    }


def test_build_condition_branch_node_template_returns_branch_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_condition_branch_node_template(
        condition="${count} > 0",
        x=100,
        y=360,
    )

    assert node.node_type == "CONDITION_BRANCH"
    assert node.name == "条件分支"
    assert node.x == 100
    assert node.y == 360
    assert node.content == {"condition": "${count} > 0"}


def test_build_param_assign_node_template_returns_assignment_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_param_assign_node_template(
        assignments=[{"name": "has_data", "value": True}],
        x=286,
        y=360,
    )

    assert node.node_type == "PARAM_ASSIGN"
    assert node.name == "参数赋值"
    assert node.content == {"assignments": [{"name": "has_data", "value": True}]}


def test_build_merge_node_template_returns_merge_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_merge_node_template(x=429, y=360)

    assert node.node_type == "MERGE"
    assert node.name == "汇聚"
    assert node.content == {}


def test_build_partition_payload_extracts_target_table_info() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    save_payload = service.build_workflow_from_template(
        service.build_sql_python_db_template(
            sql="SELECT * FROM demo",
            python_script="print('ok')",
            source_connection_name="src",
            source_datasource_type="mysql",
            target_connection_name="dst",
            target_datasource_type="postgresql",
            target_schema="public",
            target_table="demo_table",
            field_transfer_items=[
                {
                    "readColumn": {"name": "id", "type": 4},
                    "writeColumn": {"name": "id", "type": 4},
                    "deleted": False,
                }
            ],
        ),
        work_name="demo",
        work_id="work-1",
    )

    payload = service.build_partition_payload(save_payload)

    assert payload == {
        "connectionName": "dst",
        "schemaName": "public",
        "tableName": "demo_table",
    }


def test_build_field_debug_payload_defaults_to_db_write_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    save_payload = service.build_workflow_from_template(
        service.build_sql_python_db_template(
            sql="SELECT * FROM demo",
            python_script="print('ok')",
            source_connection_name="src",
            source_datasource_type="mysql",
            target_connection_name="dst",
            target_datasource_type="postgresql",
            target_schema="public",
            target_table="demo_table",
            field_transfer_items=[
                {
                    "readColumn": {"name": "id", "type": 4},
                    "writeColumn": {"name": "id", "type": 4},
                    "deleted": False,
                }
            ],
        ),
        work_name="demo",
        work_id="work-1",
    )

    payload = service.build_field_debug_payload(save_payload, preview_type="TARGET")
    data_flow = save_payload["workBook"]["nodes"][0]["value"]
    write_node = next(node for node in data_flow["nodes"] if node["nodeType"] == "DB_WRITE")

    assert payload["node"]["type"] == "DATA_FLOW"
    assert payload["paramEntity"]["workParams"][0]["name"] == "workname"
    assert payload["paramEntity"]["workParams"][0]["value"] == "demo"
    assert payload["previewOptions"] == {
        "chosenNodeId": write_node["nodeContent"]["id"],
        "previewType": "TARGET",
    }


def test_build_field_debug_payload_rejects_missing_db_write_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError, match="DATA_FLOW does not contain node type DB_WRITE"):
        service.build_field_debug_payload(
            {
                "workBook": {
                    "name": "demo",
                    "nodes": [
                        {
                            "type": "DATA_FLOW",
                            "value": {
                                "nodes": [
                                    {
                                        "nodeType": "SQL_SCRIPT",
                                        "nodeContent": {"id": "node-sql"},
                                    }
                                ]
                            },
                        }
                    ],
                }
            }
        )


def test_build_partition_payload_rejects_non_data_flow_root() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError, match="save_payload first node is not DATA_FLOW"):
        service.build_partition_payload(
            {
                "workBook": {
                    "nodes": [
                        {
                            "type": "SQL_SCRIPT",
                            "value": {},
                        }
                    ]
                }
            }
        )


def test_build_workflow_from_template_rejects_empty_work_name() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_sql_to_python_template(
        sql="SELECT 1",
        python_script="print('ok')",
    )

    with pytest.raises(FDLError, match="work_name cannot be empty"):
        service.build_workflow_from_template(template, work_name="")


def test_build_sql_script_node_template_returns_script_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_sql_script_node_template(
        sql="SELECT * FROM demo",
        connection_name="finedb",
        datasource_type="mysql",
        x=80,
        y=120,
    )

    assert node.node_type == "SQL_SCRIPT"
    assert node.name == "SQL脚本"
    assert node.x == 80
    assert node.y == 120
    assert node.content == {
        "sql": "SELECT * FROM demo",
        "connectionName": "finedb",
        "datasourceType": "mysql",
    }


def test_build_sql_to_python_template_returns_composed_template() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_sql_to_python_template(
        sql="SELECT * FROM demo",
        python_script="print('ok')",
        connection_name="finedb",
        datasource_type="mysql",
    )

    assert template.data_flow.name == "SQL转Python"
    assert list(template.data_flow.nodes) == ["sql", "python"]
    assert template.data_flow.nodes["sql"].node_type == "SQL_SCRIPT"
    assert template.data_flow.nodes["python"].node_type == "PYTHON_SCRIPT"
    assert template.data_flow.lines[0].from_node_key == "sql"
    assert template.data_flow.lines[0].to_node_key == "python"


def test_build_db_to_db_template_exposes_intermediate_representation() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_db_to_db_template(
        DBToDBWorkflowSpec(
            work_name="抓包测试",
            source_connection_name="finedb",
            source_datasource_type="mysql",
            source_sql="SELECT 1",
            target_connection_name="访客系统",
            target_datasource_type="postgresql",
            target_schema="information_schema",
            target_table="demo_table",
            field_transfer_items=[
                {
                    "readColumn": {"name": "Host", "type": 1},
                    "writeColumn": {"name": "Host", "type": 1},
                    "deleted": False,
                }
            ],
        )
    )

    assert isinstance(template, WorkflowTemplate)
    assert template.data_flow.name == "数据转换"
    assert set(template.data_flow.nodes) == {"read", "write"}
    assert template.data_flow.nodes["read"].node_type == "DB_READ"
    assert template.data_flow.nodes["write"].node_type == "DB_WRITE"
    assert template.data_flow.lines[0].from_node_key == "read"
    assert template.data_flow.lines[0].to_node_key == "write"


def test_build_sql_python_db_template_returns_three_stage_template() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_sql_python_db_template(
        sql="SELECT * FROM demo",
        python_script="print('ok')",
        source_connection_name="finedb",
        source_datasource_type="mysql",
        target_connection_name="dst",
        target_datasource_type="postgresql",
        target_schema="public",
        target_table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "id", "type": 4},
                "writeColumn": {"name": "id", "type": 4},
                "deleted": False,
            }
        ],
    )

    assert template.data_flow.name == "SQL-Python-DB"
    assert list(template.data_flow.nodes) == ["sql", "python", "write"]
    assert template.data_flow.nodes["write"].node_type == "DB_WRITE"
    assert len(template.data_flow.lines) == 2
    assert template.data_flow.lines[1].from_node_key == "python"
    assert template.data_flow.lines[1].to_node_key == "write"


def test_build_python_script_node_template_returns_script_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_python_script_node_template(
        script="print('hello')",
        x=90,
        y=240,
    )

    assert node.node_type == "PYTHON_SCRIPT"
    assert node.name == "Python脚本"
    assert node.x == 90
    assert node.y == 240
    assert node.content == {
        "script": "print('hello')",
        "runtime": "python",
    }


def test_build_condition_call_task_template_creates_branching_call_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_condition_call_task_template(
        condition="${count} > 0",
        true_called_work_name="sync_a",
        false_called_work_name="sync_b",
    )

    assert template.data_flow.name == "条件调用任务链路"
    assert list(template.data_flow.nodes) == ["branch", "call_true", "call_false"]
    assert template.data_flow.nodes["call_true"].node_type == "CALL_TASK"
    assert template.data_flow.nodes["call_false"].node_type == "CALL_TASK"
    assert template.data_flow.lines[0].line_condition == "ON_TRUE"
    assert template.data_flow.lines[1].line_condition == "ON_FALSE"


def test_build_condition_sql_python_template_creates_branching_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_condition_sql_python_template(
        condition="${count} > 0",
        success_sql="SELECT * FROM demo",
        failure_python_script="print('empty')",
        success_connection_name="finedb",
        success_datasource_type="mysql",
    )

    assert template.data_flow.name == "条件分支链路"
    assert list(template.data_flow.nodes) == ["branch", "sql", "python"]
    assert template.data_flow.nodes["branch"].node_type == "CONDITION_BRANCH"
    assert len(template.data_flow.lines) == 2
    assert template.data_flow.lines[0].line_condition == "ON_TRUE"
    assert template.data_flow.lines[1].line_condition == "ON_FALSE"


def test_build_condition_param_merge_template_creates_branch_merge_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_condition_param_merge_template(
        condition="${count} > 0",
        true_assignments=[{"name": "has_data", "value": True}],
        false_assignments=[{"name": "has_data", "value": False}],
    )

    assert template.data_flow.name == "条件参数汇聚链路"
    assert list(template.data_flow.nodes) == ["branch", "assign_true", "assign_false", "merge"]
    assert template.data_flow.nodes["assign_true"].node_type == "PARAM_ASSIGN"
    assert template.data_flow.nodes["assign_false"].node_type == "PARAM_ASSIGN"
    assert template.data_flow.nodes["merge"].node_type == "MERGE"
    assert len(template.data_flow.lines) == 4
    assert template.data_flow.lines[0].line_condition == "ON_TRUE"
    assert template.data_flow.lines[1].line_condition == "ON_FALSE"
    assert template.data_flow.lines[2].to_node_key == "merge"
    assert template.data_flow.lines[3].to_node_key == "merge"


def test_build_row_filter_node_template_rejects_empty_condition() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_row_filter_node_template(condition="")

    assert err.value.code == "FDL_TASK_INVALID_INPUT"



def test_build_field_select_node_template_returns_selected_fields() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_field_select_node_template(
        selected_fields=[
            {"sourceField": "id", "targetField": "order_id"},
            {"sourceField": "amount", "targetField": "order_amount"},
        ]
    )

    assert node.node_type == "FIELD_SELECT"
    assert len(node.content["selectedFields"]) == 2
    assert node.content["selectedFields"][0]["targetField"] == "order_id"



def test_build_sort_node_template_normalizes_order() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_sort_node_template(
        sort_fields=[
            {"field": "dt", "order": "desc"},
            {"field": "id"},
        ]
    )

    assert node.node_type == "SORT"
    assert node.content["sortFields"] == [
        {"field": "dt", "order": "DESC"},
        {"field": "id", "order": "ASC"},
    ]



def test_build_aggregate_node_template_returns_group_and_aggregations() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_aggregate_node_template(
        group_fields=["dept"],
        aggregations=[
            {"field": "amount", "function": "SUM", "as": "total_amount"}
        ],
    )

    assert node.node_type == "AGGREGATE"
    assert node.content == {
        "groupFields": ["dept"],
        "aggregations": [{"field": "amount", "function": "SUM", "as": "total_amount"}],
    }



def test_build_file_input_node_template_returns_file_source_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_file_input_node_template(
        path="/data/in/orders.csv",
        file_format="csv",
        delimiter="|",
        encoding="gbk",
        has_header=False,
        sheet_name="Sheet1",
    )

    assert node.node_type == "FILE_INPUT"
    assert node.content == {
        "path": "/data/in/orders.csv",
        "fileFormat": "CSV",
        "delimiter": "|",
        "encoding": "gbk",
        "hasHeader": False,
        "sheetName": "Sheet1",
    }



def test_build_file_output_node_template_returns_file_target_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_file_output_node_template(
        path="/data/out/orders.csv",
        file_format="csv",
        include_header=False,
        overwrite=False,
    )

    assert node.node_type == "FILE_OUTPUT"
    assert node.content["path"] == "/data/out/orders.csv"
    assert node.content["fileFormat"] == "CSV"
    assert node.content["includeHeader"] is False
    assert node.content["overwrite"] is False



def test_build_file_transfer_node_template_normalizes_transfer_mode() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_file_transfer_node_template(
        source_path="/data/in/orders.csv",
        target_path="/data/archive/orders.csv",
        transfer_mode="move",
        overwrite=False,
    )

    assert node.node_type == "FILE_TRANSFER"
    assert node.content == {
        "sourcePath": "/data/in/orders.csv",
        "targetPath": "/data/archive/orders.csv",
        "transferMode": "MOVE",
        "overwrite": False,
    }



def test_build_file_transfer_node_template_rejects_invalid_mode() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_file_transfer_node_template(
            source_path="/data/in/orders.csv",
            target_path="/data/archive/orders.csv",
            transfer_mode="link",
        )

    assert err.value.code == "FDL_TASK_INVALID_INPUT"



def test_build_db_write_node_template_returns_reusable_write_node() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    node = service.build_db_write_node_template(
        datasource_type="postgresql",
        connection_name="访客系统",
        schema="information_schema",
        table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "Host", "type": 1},
                "writeColumn": {"name": "Host", "type": 1},
                "deleted": False,
            }
        ],
        logical_primary_key=["Host"],
        update_strategy=2,
        partition_fields=["dt"],
        partition_config={"mode": "DAY"},
        distribute_config={"bucket": 4},
        write_config={"batchSize": 500},
        sync_mode="UPSERT",
        x=286,
        y=48,
    )

    assert node.node_type == "DB_WRITE"
    assert node.name == "DB表输出"
    assert node.x == 286
    assert node.y == 48
    assert node.content["type"] == "POSTGRESQL_WRITE"
    assert node.content["toConnectionName"] == "访客系统"
    assert node.content["toSchema"] == "information_schema"
    assert node.content["toTable"] == "demo_table"
    assert node.content["fieldTransferItems"][0]["readColumn"]["name"] == "Host"
    assert node.content["writeConfig"]["logicalPrimaryKey"] == ["Host"]
    assert node.content["writeConfig"]["updateStrategy"] == 2
    assert node.content["writeConfig"]["syncMode"] == "UPSERT"
    assert node.content["writeConfig"]["batchSize"] == 500
    assert node.content["partitionFields"] == ["dt"]
    assert node.content["partitionConfig"] == {"mode": "DAY"}
    assert node.content["distributeConfig"] == {"bucket": 4}


def test_build_sync_mode_config_rejects_unknown_mode() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_sync_mode_config(sync_mode="BAD_MODE")

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_row_filter_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_row_filter_template(
        source_sql="SELECT id, amount FROM ods_orders",
        condition="amount > 100",
    )

    assert template.data_flow.name == "行过滤链路"
    assert list(template.data_flow.nodes) == ["source", "filter"]
    assert template.data_flow.nodes["filter"].node_type == "ROW_FILTER"



def test_build_field_select_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_field_select_template(
        source_sql="SELECT id, amount FROM ods_orders",
        selected_fields=[{"sourceField": "id", "targetField": "order_id"}],
    )

    assert template.data_flow.name == "字段选择链路"
    assert list(template.data_flow.nodes) == ["source", "select"]
    assert template.data_flow.nodes["select"].node_type == "FIELD_SELECT"



def test_build_sort_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_sort_template(
        source_sql="SELECT id, dt FROM ods_orders",
        sort_fields=[{"field": "dt", "order": "DESC"}],
    )

    assert template.data_flow.name == "排序链路"
    assert list(template.data_flow.nodes) == ["source", "sort"]
    assert template.data_flow.nodes["sort"].node_type == "SORT"



def test_build_aggregate_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_aggregate_template(
        source_sql="SELECT dept, amount FROM ods_orders",
        group_fields=["dept"],
        aggregations=[{"field": "amount", "function": "SUM", "as": "total_amount"}],
    )

    assert template.data_flow.name == "聚合链路"
    assert list(template.data_flow.nodes) == ["source", "aggregate"]
    assert template.data_flow.nodes["aggregate"].node_type == "AGGREGATE"



def test_build_file_to_db_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_file_to_db_template(
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
            }
        ],
        sync_mode="UPSERT",
        logical_primary_key=["id"],
    )

    assert template.data_flow.name == "文件到数据库"
    assert list(template.data_flow.nodes) == ["file", "write"]
    assert template.data_flow.nodes["file"].node_type == "FILE_INPUT"
    assert template.data_flow.nodes["write"].content["writeConfig"]["syncMode"] == "UPSERT"
    assert template.data_flow.lines[0].from_node_key == "file"
    assert template.data_flow.lines[0].to_node_key == "write"



def test_build_db_to_file_template_creates_linear_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_db_to_file_template(
        source_sql="SELECT id, amount FROM ods_orders",
        target_path="/data/out/orders.csv",
        target_file_format="csv",
        connection_name="source_conn",
        datasource_type="mysql",
    )

    assert template.data_flow.name == "数据库到文件"
    assert list(template.data_flow.nodes) == ["read", "file"]
    assert template.data_flow.nodes["read"].node_type == "DB_READ"
    assert template.data_flow.nodes["file"].node_type == "FILE_OUTPUT"



def test_build_file_transfer_template_creates_single_node_flow() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_file_transfer_template(
        source_path="/data/in/orders.csv",
        target_path="/data/archive/orders.csv",
        transfer_mode="COPY",
    )

    assert template.data_flow.name == "文件传输链路"
    assert list(template.data_flow.nodes) == ["transfer"]
    assert template.data_flow.nodes["transfer"].node_type == "FILE_TRANSFER"
    assert template.data_flow.lines == []



def test_build_workflow_from_template_renders_intermediate_representation() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_db_to_db_template(
        DBToDBWorkflowSpec(
            work_name="抓包测试",
            source_connection_name="finedb",
            source_datasource_type="mysql",
            source_sql="SELECT 1",
            target_connection_name="访客系统",
            target_datasource_type="postgresql",
            target_schema="information_schema",
            target_table="demo_table",
            field_transfer_items=[
                {
                    "readColumn": {"name": "Host", "type": 1},
                    "writeColumn": {"name": "Host", "type": 1},
                    "deleted": False,
                }
            ],
            work_id="work-1",
        )
    )

    payload = service.build_workflow_from_template(template, work_name="抓包测试", work_id="work-1")

    assert payload["workId"] == "work-1"
    assert payload["workBook"]["name"] == "抓包测试"
    assert payload["workBook"]["nodes"][0]["value"]["name"] == "数据转换"
    assert payload["workBook"]["nodes"][0]["value"]["nodes"][0]["nodeType"] == "DB_READ"
    assert payload["workBook"]["nodes"][0]["value"]["nodes"][1]["nodeType"] == "DB_WRITE"


def test_build_sql_to_db_template_exposes_named_spec_family() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = service.build_sql_to_db_template(
        SQLToDBWorkflowSpec(
            work_name="抓包测试",
            source_connection_name="finedb",
            source_datasource_type="mysql",
            source_sql="SELECT 1",
            target_connection_name="访客系统",
            target_datasource_type="postgresql",
            target_schema="information_schema",
            target_table="demo_table",
            field_transfer_items=[
                {
                    "readColumn": {"name": "Host", "type": 1},
                    "writeColumn": {"name": "Host", "type": 1},
                    "deleted": False,
                }
            ],
        )
    )

    assert isinstance(template, WorkflowTemplate)
    assert set(template.data_flow.nodes) == {"read", "write"}
    assert template.data_flow.nodes["read"].node_type == "DB_READ"
    assert template.data_flow.nodes["write"].node_type == "DB_WRITE"


def test_workflow_template_from_dict_restores_template() -> None:
    template = DevService.workflow_template_from_dict(
        {
            "data_flow": {
                "name": "dict-template",
                "nodes": {
                    "sql": {
                        "node_type": "SQL_SCRIPT",
                        "name": "SQL脚本",
                        "x": 0,
                        "y": 0,
                        "content": {
                            "sql": "SELECT 1",
                            "connectionName": "",
                            "datasourceType": "",
                        },
                    },
                    "python": {
                        "node_type": "PYTHON_SCRIPT",
                        "name": "Python脚本",
                        "x": 100,
                        "y": 0,
                        "content": {
                            "script": "print('ok')",
                            "runtime": "python",
                        },
                    },
                },
                "lines": [
                    {
                        "from_node_key": "sql",
                        "to_node_key": "python",
                    }
                ],
            }
        }
    )

    assert template.data_flow.name == "dict-template"
    assert template.data_flow.nodes["sql"].node_type == "SQL_SCRIPT"
    assert template.data_flow.nodes["python"].node_type == "PYTHON_SCRIPT"
    assert template.data_flow.lines[0].from_node_key == "sql"
    assert template.data_flow.lines[0].to_node_key == "python"


    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = WorkflowTemplate(
        data_flow=service.build_db_to_db_template(
            DBToDBWorkflowSpec(
                work_name="demo",
                source_connection_name="src",
                source_datasource_type="mysql",
                source_sql="SELECT 1",
                target_connection_name="dst",
                target_datasource_type="postgresql",
                target_schema="public",
                target_table="demo_table",
                field_transfer_items=[
                    {
                        "readColumn": {"name": "id", "type": 4},
                        "writeColumn": {"name": "id", "type": 4},
                        "deleted": False,
                    }
                ],
            )
        ).data_flow.__class__(
            name="脚本链路",
            nodes={
                "sql": service.build_sql_script_node_template(
                    sql="SELECT * FROM demo",
                    connection_name="finedb",
                    datasource_type="mysql",
                ),
                "python": service.build_python_script_node_template(
                    script="print('ok')",
                ),
            },
            lines=[WorkflowLineTemplate(from_node_key="sql", to_node_key="python")],
        )
    )

    payload = service.build_workflow_from_template(template, work_name="demo", work_id="work-1")
    rendered_nodes = payload["workBook"]["nodes"][0]["value"]["nodes"]
    rendered_lines = payload["workBook"]["nodes"][0]["value"]["lines"]

    assert rendered_nodes[0]["nodeType"] == "SQL_SCRIPT"
    assert rendered_nodes[0]["nodeContent"]["sql"] == "SELECT * FROM demo"
    assert rendered_nodes[1]["nodeType"] == "PYTHON_SCRIPT"
    assert rendered_nodes[1]["nodeContent"]["script"] == "print('ok')"
    assert rendered_lines[0]["value"]["lineCondition"] == "ON_SUCCESS"
    assert rendered_lines[0]["value"]["from"] == rendered_nodes[0]["nodeContent"]["id"]
    assert rendered_lines[0]["value"]["to"] == rendered_nodes[1]["nodeContent"]["id"]


def test_build_db_to_db_workflow_matches_expected_shape() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    payload = service.build_db_to_db_workflow(
        work_id="work-1",
        work_name="抓包测试",
        source_connection_name="finedb",
        source_datasource_type="mysql",
        source_sql="SELECT 1",
        target_connection_name="访客系统",
        target_datasource_type="postgresql",
        target_schema="information_schema",
        target_table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "Host", "type": 1},
                "writeColumn": {"name": "Host", "type": 1},
                "deleted": False,
            }
        ],
    )

    assert payload["workId"] == "work-1"
    assert payload["checkState"] == "SUCCESS"
    assert payload["workBook"]["id"] == "work-1"
    assert payload["workBook"]["name"] == "抓包测试"

    data_flow = payload["workBook"]["nodes"][0]
    assert data_flow["type"] == "DATA_FLOW"
    assert data_flow["value"]["name"] == "数据转换"
    assert len(data_flow["value"]["nodes"]) == 2

    read_node = data_flow["value"]["nodes"][0]
    assert read_node["nodeType"] == "DB_READ"
    assert read_node["nodeContent"]["fromConnectionName"] == "finedb"
    assert read_node["nodeContent"]["dataBaseConfig"] == {"type": "SQL", "sql": "SELECT 1"}

    write_node = data_flow["value"]["nodes"][1]
    assert write_node["nodeType"] == "DB_WRITE"
    assert write_node["nodeContent"]["type"] == "POSTGRESQL_WRITE"
    assert write_node["nodeContent"]["toConnectionName"] == "访客系统"
    assert write_node["nodeContent"]["toSchema"] == "information_schema"
    assert write_node["nodeContent"]["toTable"] == "demo_table"
    assert write_node["nodeContent"]["fieldTransferItems"][0]["readColumn"]["name"] == "Host"

    line = data_flow["value"]["lines"][0]["value"]
    assert line["from"] == read_node["nodeContent"]["id"]
    assert line["to"] == write_node["nodeContent"]["id"]
    assert line["lineCondition"] == "ON_SUCCESS"


def test_build_workflow_from_template_preserves_node_metadata() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    template = WorkflowTemplate(
        data_flow=service.build_db_to_db_template(
            DBToDBWorkflowSpec(
                work_name="demo",
                source_connection_name="src",
                source_datasource_type="mysql",
                source_sql="SELECT 1",
                target_connection_name="dst",
                target_datasource_type="postgresql",
                target_schema="public",
                target_table="demo_table",
                field_transfer_items=[
                    {
                        "readColumn": {"name": "id", "type": 4},
                        "writeColumn": {"name": "id", "type": 4},
                        "deleted": False,
                    }
                ],
            )
        ).data_flow
    )
    read_node = template.data_flow.nodes["read"]
    template = WorkflowTemplate(
        data_flow=template.data_flow.__class__(
            name=template.data_flow.name,
            nodes={
                "read": read_node.__class__(
                    node_type=read_node.node_type,
                    name="自定义输入",
                    x=read_node.x,
                    y=read_node.y,
                    content=read_node.content,
                    note="读取源数据",
                    execute_logic="OR",
                    disabled=True,
                ),
                "write": template.data_flow.nodes["write"],
            },
            lines=template.data_flow.lines,
            note=template.data_flow.note,
            execute_logic=template.data_flow.execute_logic,
            disabled=template.data_flow.disabled,
        )
    )

    payload = service.build_workflow_from_template(template, work_name="demo", work_id="work-1")
    rendered_read_node = payload["workBook"]["nodes"][0]["value"]["nodes"][0]

    assert rendered_read_node["nodeContent"]["name"] == "自定义输入"
    assert rendered_read_node["nodeContent"]["note"] == "读取源数据"
    assert rendered_read_node["nodeContent"]["executeLogic"] == "OR"
    assert rendered_read_node["nodeContent"]["disabled"] is True


def test_build_publish_payload_wraps_save_payload() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    save_payload = {"workId": "work-1"}
    payload = service.build_publish_payload(save_payload, describe="发布描述", sub_work_ids=["child-1"])

    assert payload == {
        "dataDevWork": {"workId": "work-1"},
        "subWorkIds": ["child-1"],
        "describe": "发布描述",
    }


def test_build_call_task_node_template_rejects_missing_target() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_call_task_node_template()

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_condition_branch_node_template_rejects_empty_condition() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_condition_branch_node_template(condition="")

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_param_assign_node_template_rejects_empty_assignments() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_param_assign_node_template(assignments=[])

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_workflow_template_rejects_missing_line_nodes() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_workflow_template(
            name="bad-template",
            nodes={
                "sql": WorkflowNodeTemplate(
                    node_type="SQL_SCRIPT",
                    name="SQL脚本",
                    x=0,
                    y=0,
                    content={"sql": "SELECT 1", "connectionName": "", "datasourceType": ""},
                )
            },
            lines=[WorkflowLineTemplate(from_node_key="sql", to_node_key="missing")],
        )

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_workflow_template_rejects_invalid_condition_branch_outgoing_lines() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_workflow_template(
            name="bad-branch",
            nodes={
                "branch": service.build_condition_branch_node_template(condition="${count} > 0"),
                "sql": service.build_sql_script_node_template(sql="SELECT 1"),
            },
            lines=[
                WorkflowLineTemplate(
                    from_node_key="branch",
                    to_node_key="sql",
                    line_condition="ON_TRUE",
                )
            ],
        )

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_workflow_template_rejects_empty_param_assignments() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_workflow_template(
            name="bad-param-assign",
            nodes={
                "assign": WorkflowNodeTemplate(
                    node_type="PARAM_ASSIGN",
                    name="参数赋值",
                    x=0,
                    y=0,
                    content={"assignments": []},
                )
            },
        )

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_workflow_template_rejects_merge_with_multiple_outgoing_lines() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_workflow_template(
            name="bad-merge",
            nodes={
                "merge": service.build_merge_node_template(),
                "sql": service.build_sql_script_node_template(sql="SELECT 1"),
                "python": service.build_python_script_node_template(script="print('ok')"),
            },
            lines=[
                WorkflowLineTemplate(from_node_key="merge", to_node_key="sql"),
                WorkflowLineTemplate(from_node_key="merge", to_node_key="python"),
            ],
        )

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_sql_script_node_template_rejects_empty_sql() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_sql_script_node_template(sql="")

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_field_debug_payload_matches_helper_shape() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    save_payload = service.build_db_to_db_workflow(
        work_id="work-1",
        work_name="demo",
        source_connection_name="src",
        source_datasource_type="mysql",
        source_sql="SELECT 1",
        target_connection_name="dst",
        target_datasource_type="postgresql",
        target_schema="public",
        target_table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "id", "type": 4},
                "writeColumn": {"name": "id", "type": 4},
                "deleted": False,
            }
        ],
    )
    payload = service.build_field_debug_payload(save_payload)

    assert payload["node"]["type"] == "DATA_FLOW"
    assert payload["paramEntity"]["workParams"][0] == {
        "name": "workname",
        "value": "demo",
        "valueType": "STRING",
    }
    assert payload["previewOptions"]["previewType"] == ""
    assert payload["previewOptions"]["chosenNodeId"] == payload["node"]["value"]["nodes"][1]["nodeContent"]["id"]


def test_build_python_script_node_template_rejects_empty_script() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_python_script_node_template(script="")

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_render_workflow_templates_batch_returns_rendered_payloads() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    items = service.render_workflow_templates_batch(
        [
            {
                "template": {
                    "data_flow": {
                        "name": "dict-template",
                        "nodes": {
                            "sql": {
                                "node_type": "SQL_SCRIPT",
                                "name": "SQL脚本",
                                "x": 0,
                                "y": 0,
                                "content": {
                                    "sql": "SELECT 1",
                                    "connectionName": "",
                                    "datasourceType": "",
                                },
                            }
                        },
                        "lines": [],
                    }
                },
                "work_name": "demo-a",
                "work_id": "work-a",
            },
            {
                "template": {
                    "data_flow": {
                        "name": "dict-template-2",
                        "nodes": {
                            "python": {
                                "node_type": "PYTHON_SCRIPT",
                                "name": "Python脚本",
                                "x": 0,
                                "y": 0,
                                "content": {
                                    "script": "print('ok')",
                                    "runtime": "python",
                                },
                            }
                        },
                        "lines": [],
                    }
                },
                "work_name": "demo-b",
            },
        ]
    )

    assert len(items) == 2
    assert items[0]["work_name"] == "demo-a"
    assert items[0]["work_id"] == "work-a"
    assert items[0]["save_payload"]["workId"] == "work-a"
    assert items[1]["work_name"] == "demo-b"
    assert items[1]["save_payload"]["workBook"]["name"] == "demo-b"


@pytest.mark.asyncio
async def test_save_workflow_templates_batch_only_calls_save_endpoint() -> None:
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/work/save"):
            return httpx.Response(200, json={"saved": True})
        raise AssertionError(request.url.path)

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            encrypt_mode="aes",
            encrypt_key="1ED6F5BA8CFD75F8",
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.save_workflow_templates_batch(
        [
            {
                "template": {
                    "data_flow": {
                        "name": "dict-template",
                        "nodes": {
                            "sql": {
                                "node_type": "SQL_SCRIPT",
                                "name": "SQL脚本",
                                "x": 0,
                                "y": 0,
                                "content": {
                                    "sql": "SELECT 1",
                                    "connectionName": "",
                                    "datasourceType": "",
                                },
                            }
                        },
                        "lines": [],
                    }
                },
                "work_name": "demo-a",
                "work_id": "work-a",
            },
            {
                "template": {
                    "data_flow": {
                        "name": "dict-template-2",
                        "nodes": {
                            "python": {
                                "node_type": "PYTHON_SCRIPT",
                                "name": "Python脚本",
                                "x": 0,
                                "y": 0,
                                "content": {
                                    "script": "print('ok')",
                                    "runtime": "python",
                                },
                            }
                        },
                        "lines": [],
                    }
                },
                "work_name": "demo-b",
            },
        ]
    )

    assert calls == [
        "/webroot/decision/fdl/dev/work/save",
        "/webroot/decision/fdl/dev/work/save",
    ]
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/save"
    assert len(data) == 2
    assert data[0]["work_name"] == "demo-a"
    assert data[0]["work_id"] == "work-a"
    assert data[0]["status_code"] == 200
    assert data[0]["endpoint"] == "/webroot/decision/fdl/dev/work/save"
    assert data[1]["work_name"] == "demo-b"
    assert data[1]["result"] == {"saved": True}
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    save_payload = service.build_db_to_db_workflow(
        work_name="demo",
        source_connection_name="src",
        source_datasource_type="mysql",
        source_sql="SELECT 1",
        target_connection_name="访客系统",
        target_datasource_type="postgresql",
        target_schema="information_schema",
        target_table="dwadwa",
        field_transfer_items=[
            {
                "readColumn": {"name": "id", "type": 4},
                "writeColumn": {"name": "id", "type": 4},
                "deleted": False,
            }
        ],
    )
    payload = service.build_partition_payload(save_payload)

    assert payload == {
        "connectionName": "访客系统",
        "schemaName": "information_schema",
        "tableName": "dwadwa",
    }


@pytest.mark.asyncio
async def test_prepare_db_to_db_workflow_calls_helper_endpoints() -> None:
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/field/target"):
            return httpx.Response(200, json={"target": True})
        if request.url.path.endswith("/field/refresh"):
            return httpx.Response(200, json={"refresh": True})
        if request.url.path.endswith("/partition/get"):
            return httpx.Response(200, json={"partition": True})
        raise AssertionError(request.url.path)

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            encrypt_mode="aes",
            encrypt_key="1ED6F5BA8CFD75F8",
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.prepare_db_to_db_workflow(
        work_id="work-1",
        work_name="demo",
        source_connection_name="src",
        source_datasource_type="mysql",
        source_sql="SELECT 1",
        target_connection_name="dst",
        target_datasource_type="postgresql",
        target_schema="public",
        target_table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "id", "type": 4},
                "writeColumn": {"name": "id", "type": 4},
                "deleted": False,
            }
        ],
        sync_mode="UPSERT",
        logical_primary_key=["id"],
        update_strategy=3,
        partition_fields=["dt"],
    )

    assert calls == [
        "/webroot/decision/fdl/dev/datasource/field/target",
        "/webroot/decision/fdl/dev/datasource/field/refresh",
        "/webroot/decision/fdl/dev/conn/table/conf/partition/get",
    ]
    assert data["target_fields"] == {"target": True}
    assert data["refreshed_fields"] == {"refresh": True}
    assert data["partition_config"] == {"partition": True}
    assert data["save_payload"]["workBook"]["nodes"][0]["value"]["nodes"][1]["nodeContent"]["writeConfig"]["syncMode"] == "UPSERT"
    assert data["save_payload"]["workBook"]["nodes"][0]["value"]["nodes"][1]["nodeContent"]["writeConfig"]["logicalPrimaryKey"] == ["id"]
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/conn/table/conf/partition/get"


@pytest.mark.asyncio
async def test_save_db_to_db_workflow_builds_and_saves() -> None:
    captured = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["body"] = request.content.decode("utf-8")
        return httpx.Response(200, json={"saved": True})

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            encrypt_mode="aes",
            encrypt_key="1ED6F5BA8CFD75F8",
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.save_db_to_db_workflow(
        work_id="work-1",
        work_name="demo",
        source_connection_name="src",
        source_datasource_type="mysql",
        source_sql="SELECT 1",
        target_connection_name="dst",
        target_datasource_type="postgresql",
        target_schema="public",
        target_table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "id", "type": 4},
                "writeColumn": {"name": "id", "type": 4},
                "deleted": False,
            }
        ],
        sync_mode="APPEND",
        logical_primary_key=["id"],
        update_strategy=1,
    )

    assert data == {"saved": True}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/save"
    assert captured["path"] == "/webroot/decision/fdl/dev/work/save"
    assert captured["body"]




@pytest.mark.asyncio
async def test_save_db_to_db_workflow_only_calls_save_endpoint() -> None:
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/work/save"):
            return httpx.Response(200, json={"saved": True})
        raise AssertionError(request.url.path)

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            encrypt_mode="aes",
            encrypt_key="1ED6F5BA8CFD75F8",
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.save_db_to_db_workflow(
        work_id="work-1",
        work_name="demo",
        source_connection_name="src",
        source_datasource_type="mysql",
        source_sql="SELECT 1",
        target_connection_name="dst",
        target_datasource_type="postgresql",
        target_schema="public",
        target_table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "id", "type": 4},
                "writeColumn": {"name": "id", "type": 4},
                "deleted": False,
            }
        ],
        sync_mode="UPSERT",
        logical_primary_key=["id"],
        update_strategy=2,
    )

    assert calls == ["/webroot/decision/fdl/dev/work/save"]
    assert data == {"saved": True}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/save"


@pytest.mark.asyncio
async def test_save_work_does_not_call_publish_or_check() -> None:
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/work/save"):
            return httpx.Response(200, json={"saved": True})
        raise AssertionError(request.url.path)

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            encrypt_mode="aes",
            encrypt_key="1ED6F5BA8CFD75F8",
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.save_work({"name": "demo"})

    assert calls == ["/webroot/decision/fdl/dev/work/save"]
    assert data == {"saved": True}
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/save"


@pytest.mark.asyncio
async def test_publish_db_to_db_workflow_runs_save_check_publish() -> None:
    calls = []

    async def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if request.url.path.endswith("/work/save"):
            return httpx.Response(200, json={"saved": True})
        if request.url.path.endswith("/work/publish/check"):
            return httpx.Response(200, json={"checked": True})
        if request.url.path.endswith("/work/publish"):
            return httpx.Response(200, json={"published": True})
        raise AssertionError(request.url.path)

    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
            encrypt_mode="aes",
            encrypt_key="1ED6F5BA8CFD75F8",
            transport=httpx.MockTransport(handler),
        )
    )

    data, status, endpoint = await service.publish_db_to_db_workflow(
        work_id="work-1",
        work_name="demo",
        source_connection_name="src",
        source_datasource_type="mysql",
        source_sql="SELECT 1",
        target_connection_name="dst",
        target_datasource_type="postgresql",
        target_schema="public",
        target_table="demo_table",
        field_transfer_items=[
            {
                "readColumn": {"name": "id", "type": 4},
                "writeColumn": {"name": "id", "type": 4},
                "deleted": False,
            }
        ],
        describe="发布",
        sync_mode="UPSERT",
        logical_primary_key=["id"],
        update_strategy=2,
    )

    assert calls == [
        "/webroot/decision/fdl/dev/work/save",
        "/webroot/decision/fdl/dev/work/publish/check",
        "/webroot/decision/fdl/dev/work/publish",
    ]
    assert data["save_result"] == {"saved": True}
    assert data["publish_check_result"] == {"checked": True}
    assert data["publish_result"] == {"published": True}
    assert data["publish_payload"]["describe"] == "发布"
    assert status == 200
    assert endpoint == "/webroot/decision/fdl/dev/work/publish"


@pytest.mark.asyncio
async def test_save_work_rejects_empty_payload() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        await service.save_work("")

    assert err.value.code == "FDL_TASK_INVALID_INPUT"


def test_build_db_to_db_workflow_rejects_empty_field_transfer_items() -> None:
    service = DevService(
        FDLClient(
            resolver=EndpointResolver(base_url="https://fdl.example.com"),
            auth_provider=AppCodeAuth("abc"),
            retry_max=0,
        )
    )

    with pytest.raises(FDLError) as err:
        service.build_db_to_db_workflow(
            work_name="demo",
            source_connection_name="src",
            source_datasource_type="mysql",
            source_sql="SELECT 1",
            target_connection_name="dst",
            target_datasource_type="postgresql",
            target_schema="public",
            target_table="demo_table",
            field_transfer_items=[],
        )

    assert err.value.code == "FDL_TASK_INVALID_INPUT"
