import pytest

from fdl_mcp.errors import FDLError
from fdl_mcp.server import App


def _build_app(monkeypatch: pytest.MonkeyPatch) -> App:
    monkeypatch.setenv("FDL_BASE_URL", "https://fdl.example.com")
    monkeypatch.setenv("FDL_AUTH_MODE", "appcode")
    monkeypatch.setenv("FDL_APPCODE", "abc")
    monkeypatch.delenv("FDL_ENCRYPT_MODE", raising=False)
    monkeypatch.delenv("FDL_ENCRYPT_KEY", raising=False)
    return App()


@pytest.mark.asyncio
async def test_app_lists_agent_template_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    tools = await app.mcp.list_tools()
    tool_names = {tool.name for tool in tools}

    assert "fdl_dev_configure_chrome_session" in tool_names
    assert "fdl_dev_list_connections" in tool_names
    assert "fdl_dev_get_connection_info" in tool_names
    assert "fdl_dev_list_connection_schemas" in tool_names
    assert "fdl_dev_list_table_views" in tool_names
    assert "fdl_dev_get_global_params" in tool_names
    assert "fdl_dev_get_development_instance_info" in tool_names
    assert "fdl_dev_list_work_versions" in tool_names
    assert "fdl_dev_get_published_work_info" in tool_names
    assert "fdl_dev_get_catalog_entity_info" in tool_names
    assert "fdl_dev_get_work_development_info" in tool_names
    assert "fdl_dev_list_functions" in tool_names
    assert "fdl_dev_get_downstream" in tool_names
    assert "fdl_dev_get_published_instance_info" in tool_names
    assert "fdl_dev_preview_datasource" in tool_names
    assert "fdl_dev_get_source_fields" in tool_names
    assert "fdl_dev_get_target_fields" in tool_names
    assert "fdl_dev_refresh_fields" in tool_names
    assert "fdl_dev_get_field_modifies" in tool_names
    assert "fdl_dev_get_partition_config" in tool_names
    assert "fdl_dev_save_work" in tool_names
    assert "fdl_dev_publish_work_check" in tool_names
    assert "fdl_dev_publish_work" in tool_names
    assert "fdl_dev_list_template_node_types" in tool_names
    assert "fdl_dev_get_workflow_template_examples" in tool_names
    assert "fdl_dev_build_workflow_template_from_dict" in tool_names
    assert "fdl_dev_validate_workflow_template" in tool_names
    assert "fdl_dev_render_workflow_template" in tool_names
    assert "fdl_dev_build_db_read_node_template" in tool_names
    assert "fdl_dev_build_api_input_node_template" in tool_names
    assert "fdl_dev_build_db_write_node_template" in tool_names
    assert "fdl_dev_build_param_output_node_template" in tool_names
    assert "fdl_dev_build_sql_script_node_template" in tool_names
    assert "fdl_dev_build_python_script_node_template" in tool_names
    assert "fdl_dev_build_file_input_node_template" in tool_names
    assert "fdl_dev_build_file_output_node_template" in tool_names
    assert "fdl_dev_build_file_transfer_node_template" in tool_names
    assert "fdl_dev_build_call_task_node_template" in tool_names
    assert "fdl_dev_build_condition_branch_node_template" in tool_names
    assert "fdl_dev_build_param_assign_node_template" in tool_names
    assert "fdl_dev_build_merge_node_template" in tool_names
    assert "fdl_dev_build_condition_param_merge_template" in tool_names
    assert "fdl_dev_build_api_to_param_output_template" in tool_names
    assert "fdl_dev_build_join_template" in tool_names
    assert "fdl_dev_build_data_compare_template" in tool_names
    assert "fdl_dev_build_union_template" in tool_names
    assert "fdl_dev_build_unpivot_template" in tool_names
    assert "fdl_dev_build_json_parse_template" in tool_names
    assert "fdl_dev_build_row_filter_template" in tool_names
    assert "fdl_dev_build_field_select_template" in tool_names
    assert "fdl_dev_build_sort_template" in tool_names
    assert "fdl_dev_build_aggregate_template" in tool_names
    assert "fdl_dev_build_file_to_db_template" in tool_names
    assert "fdl_dev_build_db_to_file_template" in tool_names
    assert "fdl_dev_build_file_transfer_template" in tool_names
    assert "fdl_dev_build_publish_payload" in tool_names
    assert "fdl_dev_build_partition_payload" in tool_names
    assert "fdl_dev_build_field_debug_payload" in tool_names


@pytest.mark.asyncio
async def test_configure_chrome_session_tool_rebuilds_runtime(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_configure_chrome_session",
        {
            "page_data": {
                "origin": "http://192.168.138.35:8068",
                "href": "http://192.168.138.35:8068/webroot/decision#preparation",
                "frontSeed": "1ED6F5BA8CFD75F8",
                "cookie": "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1",
            }
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_configure_chrome_session"
    assert data["data"] == {
        "base_url": "http://192.168.138.35:8068",
        "auth_mode": "fine_auth_token",
        "encrypt_mode": "aes",
        "chrome_session_mode": True,
        "chrome_session_page_url": "http://192.168.138.35:8068/webroot/decision#preparation",
        "has_fine_auth_token": True,
        "has_cookie_header": True,
        "has_encrypt_key": True,
    }
    assert app.settings.base_url == "http://192.168.138.35:8068"
    assert app.settings.fine_auth_token == "demo-token"
    assert app.settings.fine_auth_cookie == "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1"
    assert app.settings.encrypt_key == "1ED6F5BA8CFD75F8"




@pytest.mark.asyncio
async def test_configure_chrome_session_tool_rejects_missing_origin(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    with pytest.raises(Exception) as err:
        await app.mcp.call_tool(
            "fdl_dev_configure_chrome_session",
            {
                "page_data": {
                    "href": "http://192.168.138.35:8068/webroot/decision#preparation",
                    "frontSeed": "1ED6F5BA8CFD75F8",
                    "cookie": "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1",
                }
            },
        )

    assert "FDL_BASE_URL is required" in str(err.value)


@pytest.mark.asyncio
async def test_configure_chrome_session_tool_rejects_missing_front_seed(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    with pytest.raises(Exception) as err:
        await app.mcp.call_tool(
            "fdl_dev_configure_chrome_session",
            {
                "page_data": {
                    "origin": "http://192.168.138.35:8068",
                    "href": "http://192.168.138.35:8068/webroot/decision#preparation",
                    "cookie": "JSESSIONID=abc; fine_auth_token=demo-token; tenant=1",
                }
            },
        )

    assert "FDL_ENCRYPT_KEY is required for aes mode" in str(err.value)


@pytest.mark.asyncio
async def test_configure_chrome_session_tool_rejects_missing_cookie_token(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    with pytest.raises(Exception) as err:
        await app.mcp.call_tool(
            "fdl_dev_configure_chrome_session",
            {
                "page_data": {
                    "origin": "http://192.168.138.35:8068",
                    "href": "http://192.168.138.35:8068/webroot/decision#preparation",
                    "frontSeed": "1ED6F5BA8CFD75F8",
                    "cookie": "JSESSIONID=abc; tenant=1",
                }
            },
        )

    assert "FDL_FINE_AUTH_TOKEN is required for fine_auth_token mode" in str(err.value)


@pytest.mark.asyncio
async def test_build_single_node_template_tools_return_serialized_nodes(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    cases = [
        (
            "fdl_dev_build_db_read_node_template",
            {
                "datasource_type": "mysql",
                "connection_name": "source_conn",
                "sql": "SELECT * FROM orders",
            },
            "DB_READ",
            "read",
        ),
        (
            "fdl_dev_build_api_input_node_template",
            {
                "url": "https://api.example.com/orders",
                "method": "post",
                "body": {"bizDate": "2026-03-09"},
            },
            "API_INPUT",
            "api",
        ),
        (
            "fdl_dev_build_db_write_node_template",
            {
                "datasource_type": "postgresql",
                "connection_name": "target_conn",
                "schema": "public",
                "table": "orders",
                "field_transfer_items": [
                    {
                        "readColumn": {"name": "id", "type": 4},
                        "writeColumn": {"name": "id", "type": 4},
                        "deleted": False,
                    }
                ],
                "sync_mode": "append",
            },
            "DB_WRITE",
            "write",
        ),
        (
            "fdl_dev_build_param_output_node_template",
            {
                "outputs": [{"name": "order_id", "sourceField": "id"}],
            },
            "PARAM_OUTPUT",
            "output",
        ),
        (
            "fdl_dev_build_sql_script_node_template",
            {
                "sql": "SELECT 1",
                "connection_name": "source_conn",
                "datasource_type": "mysql",
            },
            "SQL_SCRIPT",
            "sql",
        ),
        (
            "fdl_dev_build_python_script_node_template",
            {
                "script": "print('ok')",
            },
            "PYTHON_SCRIPT",
            "python",
        ),
        (
            "fdl_dev_build_file_input_node_template",
            {
                "path": "/data/in/orders.csv",
                "file_format": "csv",
            },
            "FILE_INPUT",
            "file",
        ),
        (
            "fdl_dev_build_file_output_node_template",
            {
                "path": "/data/out/orders.csv",
                "file_format": "csv",
                "overwrite": False,
            },
            "FILE_OUTPUT",
            "file",
        ),
        (
            "fdl_dev_build_file_transfer_node_template",
            {
                "source_path": "/data/in/orders.csv",
                "target_path": "/data/archive/orders.csv",
                "transfer_mode": "move",
            },
            "FILE_TRANSFER",
            "transfer",
        ),
        (
            "fdl_dev_build_call_task_node_template",
            {
                "called_work_name": "daily_sync",
            },
            "CALL_TASK",
            "call",
        ),
        (
            "fdl_dev_build_condition_branch_node_template",
            {
                "condition": "${count} > 0",
            },
            "CONDITION_BRANCH",
            "branch",
        ),
        (
            "fdl_dev_build_param_assign_node_template",
            {
                "assignments": [{"name": "has_data", "value": True}],
            },
            "PARAM_ASSIGN",
            "assign",
        ),
        (
            "fdl_dev_build_merge_node_template",
            {},
            "MERGE",
            "merge",
        ),
    ]

    for tool_name, params, expected_node_type, expected_endpoint_suffix in cases:
        _, data = await app.mcp.call_tool(tool_name, params)
        assert data["ok"] is True
        assert data["endpoint"] == f"local://{tool_name}"
        assert data["data"]["node_type"] == expected_node_type
        if expected_endpoint_suffix == "api":
            assert data["data"]["content"]["request"]["method"] == "POST"
        if expected_endpoint_suffix == "write":
            assert data["data"]["content"]["writeConfig"]["syncMode"] == "APPEND"
        if expected_endpoint_suffix == "file" and expected_node_type == "FILE_OUTPUT":
            assert data["data"]["content"]["overwrite"] is False
        if expected_endpoint_suffix == "transfer":
            assert data["data"]["content"]["transferMode"] == "MOVE"


@pytest.mark.asyncio
async def test_list_template_node_types_returns_agent_schema(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool("fdl_dev_list_template_node_types", {})

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_list_template_node_types"
    assert {item["node_type"] for item in data["data"]["node_types"]} == {
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


@pytest.mark.asyncio
async def test_get_workflow_template_examples_returns_examples(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool("fdl_dev_get_workflow_template_examples", {})

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_get_workflow_template_examples"
    assert set(data["data"]["examples"]) == {
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
    assert data["data"]["examples"]["sql_to_python"]["data_flow"]["nodes"]["sql"]["node_type"] == "SQL_SCRIPT"
    assert data["data"]["recommended_flow"][0] == "fdl_dev_list_template_node_types"


@pytest.mark.asyncio
async def test_build_api_to_param_output_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_api_to_param_output_template",
        {
            "api_url": "https://api.example.com/orders",
            "output_fields": ["order_id", "status"],
            "method": "POST",
            "body": {"date": "2026-03-07"},
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_api_to_param_output_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["api"]["node_type"] == "API_INPUT"
    assert nodes["api"]["content"]["request"]["method"] == "POST"
    assert nodes["output"]["node_type"] == "PARAM_OUTPUT"
    assert nodes["output"]["content"]["outputs"] == [
        {"name": "order_id", "sourceField": "order_id"},
        {"name": "status", "sourceField": "status"},
    ]


@pytest.mark.asyncio
async def test_build_api_to_param_output_template_rejects_empty_output_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    with pytest.raises(Exception) as err:
        await app.mcp.call_tool(
            "fdl_dev_build_api_to_param_output_template",
            {
                "api_url": "https://api.example.com/orders",
                "output_fields": [],
            },
        )

    assert "outputs cannot be empty" in str(err.value)


@pytest.mark.asyncio
async def test_build_join_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_join_template",
        {
            "left_sql": "SELECT id, amount FROM orders",
            "right_sql": "SELECT id, level FROM users",
            "left_keys": ["id"],
            "right_keys": ["id"],
            "join_type": "left",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_join_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["join"]["node_type"] == "JOIN"
    assert nodes["join"]["content"] == {
        "joinType": "LEFT",
        "leftKeys": ["id"],
        "rightKeys": ["id"],
    }


@pytest.mark.asyncio
async def test_build_data_compare_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_data_compare_template",
        {
            "left_sql": "SELECT id, dt FROM ods_orders",
            "right_sql": "SELECT id, dt FROM dwd_orders",
            "compare_keys": ["id"],
            "include_equal_rows": False,
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_data_compare_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["compare"]["node_type"] == "DATA_COMPARE"
    assert nodes["compare"]["content"] == {
        "compareKeys": ["id"],
        "includeEqualRows": False,
    }


@pytest.mark.asyncio
async def test_build_union_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_union_template",
        {
            "upstream_sqls": ["SELECT id FROM a", "SELECT id FROM b"],
            "union_mode": "distinct",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_union_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["union"]["node_type"] == "UNION"
    assert nodes["union"]["content"] == {"unionMode": "DISTINCT"}


@pytest.mark.asyncio
async def test_build_union_template_rejects_single_source(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    with pytest.raises(Exception) as err:
        await app.mcp.call_tool(
            "fdl_dev_build_union_template",
            {
                "upstream_sqls": ["SELECT 1"],
            },
        )

    assert "at least two SQL statements" in str(err.value)


@pytest.mark.asyncio
async def test_build_unpivot_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_unpivot_template",
        {
            "source_sql": "SELECT id, pv, uv FROM ads_daily_metrics",
            "index_fields": ["id"],
            "value_fields": ["pv", "uv"],
            "variable_field_name": "metric",
            "value_field_name": "value",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_unpivot_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["unpivot"]["node_type"] == "UNPIVOT"
    assert nodes["unpivot"]["content"] == {
        "indexFields": ["id"],
        "valueFields": ["pv", "uv"],
        "variableFieldName": "metric",
        "valueFieldName": "value",
    }


@pytest.mark.asyncio
async def test_build_json_parse_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_json_parse_template",
        {
            "source_sql": "SELECT id, ext_json FROM ods_orders",
            "source_field": "ext_json",
            "target_fields": [
                {"name": "province", "jsonPath": "$.address.province"},
                {"name": "city", "jsonPath": "$.address.city"},
            ],
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_json_parse_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["json_parse"]["node_type"] == "JSON_PARSE"
    assert nodes["json_parse"]["content"]["sourceField"] == "ext_json"
    assert len(nodes["json_parse"]["content"]["targetFields"]) == 2


@pytest.mark.asyncio
async def test_build_row_filter_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_row_filter_template",
        {
            "source_sql": "SELECT id, amount FROM ods_orders",
            "condition": "amount > 100",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_row_filter_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["filter"]["node_type"] == "ROW_FILTER"
    assert nodes["filter"]["content"] == {"condition": "amount > 100"}


@pytest.mark.asyncio
async def test_build_field_select_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_field_select_template",
        {
            "source_sql": "SELECT id, amount FROM ods_orders",
            "selected_fields": [
                {"sourceField": "id", "targetField": "order_id"},
                {"sourceField": "amount", "targetField": "order_amount"},
            ],
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_field_select_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["select"]["node_type"] == "FIELD_SELECT"
    assert len(nodes["select"]["content"]["selectedFields"]) == 2


@pytest.mark.asyncio
async def test_build_sort_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_sort_template",
        {
            "source_sql": "SELECT id, dt FROM ods_orders",
            "sort_fields": [{"field": "dt", "order": "desc"}],
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_sort_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["sort"]["node_type"] == "SORT"
    assert nodes["sort"]["content"]["sortFields"] == [{"field": "dt", "order": "DESC"}]


@pytest.mark.asyncio
async def test_build_aggregate_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_aggregate_template",
        {
            "source_sql": "SELECT dept, amount FROM ods_orders",
            "group_fields": ["dept"],
            "aggregations": [{"field": "amount", "function": "SUM", "as": "total_amount"}],
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_aggregate_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["aggregate"]["node_type"] == "AGGREGATE"
    assert nodes["aggregate"]["content"] == {
        "groupFields": ["dept"],
        "aggregations": [{"field": "amount", "function": "SUM", "as": "total_amount"}],
    }


@pytest.mark.asyncio
async def test_build_file_to_db_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_file_to_db_template",
        {
            "file_path": "/data/in/orders.csv",
            "file_format": "csv",
            "target_connection_name": "target_conn",
            "target_datasource_type": "postgresql",
            "target_schema": "public",
            "target_table": "orders_stage",
            "field_transfer_items": [
                {
                    "readColumn": {"name": "id", "type": 4},
                    "writeColumn": {"name": "id", "type": 4},
                    "deleted": False,
                }
            ],
            "sync_mode": "UPSERT",
            "logical_primary_key": ["id"],
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_file_to_db_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["file"]["node_type"] == "FILE_INPUT"
    assert nodes["file"]["content"]["path"] == "/data/in/orders.csv"
    assert nodes["write"]["node_type"] == "DB_WRITE"
    assert nodes["write"]["content"]["writeConfig"]["syncMode"] == "UPSERT"
    assert nodes["write"]["content"]["writeConfig"]["logicalPrimaryKey"] == ["id"]


@pytest.mark.asyncio
async def test_build_db_to_file_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_db_to_file_template",
        {
            "source_sql": "SELECT id, amount FROM ods_orders",
            "target_path": "/data/out/orders.csv",
            "target_file_format": "csv",
            "connection_name": "source_conn",
            "datasource_type": "mysql",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_db_to_file_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["read"]["node_type"] == "DB_READ"
    assert nodes["file"]["node_type"] == "FILE_OUTPUT"
    assert nodes["file"]["content"]["path"] == "/data/out/orders.csv"
    assert nodes["file"]["content"]["fileFormat"] == "CSV"


@pytest.mark.asyncio
async def test_build_file_transfer_template_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_file_transfer_template",
        {
            "source_path": "/data/in/orders.csv",
            "target_path": "/data/archive/orders.csv",
            "transfer_mode": "move",
            "overwrite": False,
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_file_transfer_template"
    nodes = data["data"]["data_flow"]["nodes"]
    assert nodes["transfer"]["node_type"] == "FILE_TRANSFER"
    assert nodes["transfer"]["content"] == {
        "sourcePath": "/data/in/orders.csv",
        "targetPath": "/data/archive/orders.csv",
        "transferMode": "MOVE",
        "overwrite": False,
    }


@pytest.mark.asyncio
async def test_build_workflow_template_from_dict_rejects_invalid_api_input_node(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    with pytest.raises(Exception) as err:
        await app.mcp.call_tool(
            "fdl_dev_build_workflow_template_from_dict",
            {
                "name": "invalid-api-template",
                "nodes": {
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
            },
        )

    assert "API_INPUT nodes must define request.url" in str(err.value)


@pytest.mark.asyncio
async def test_build_workflow_template_from_dict_rejects_invalid_param_output_node(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_partition_payload",
        {
            "save_payload": {
                "workId": "work-1",
                "workBook": {
                    "name": "demo",
                    "nodes": [
                        {
                            "type": "DATA_FLOW",
                            "value": {
                                "nodes": [
                                    {
                                        "nodeType": "DB_WRITE",
                                        "nodeContent": {
                                            "id": "node-write",
                                            "toConnectionName": "dst",
                                            "toSchema": "public",
                                            "toTable": "demo_table",
                                        },
                                    }
                                ]
                            },
                        }
                    ],
                },
            }
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_partition_payload"
    assert data["data"] == {
        "connectionName": "dst",
        "schemaName": "public",
        "tableName": "demo_table",
    }


@pytest.mark.asyncio
async def test_build_field_debug_payload_tool_returns_field_request(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_field_debug_payload",
        {
            "save_payload": {
                "workId": "work-1",
                "workBook": {
                    "name": "demo",
                    "nodes": [
                        {
                            "type": "DATA_FLOW",
                            "value": {
                                "nodes": [
                                    {
                                        "nodeType": "SQL_SCRIPT",
                                        "nodeContent": {"id": "node-sql", "name": "SQL脚本"},
                                    },
                                    {
                                        "nodeType": "DB_WRITE",
                                        "nodeContent": {
                                            "id": "node-write",
                                            "name": "DB表输出",
                                            "toConnectionName": "dst",
                                            "toSchema": "public",
                                            "toTable": "demo_table",
                                        },
                                    },
                                ],
                                "lines": [],
                                "id": "df-1",
                                "name": "数据转换",
                            },
                        }
                    ],
                },
            },
            "preview_type": "TARGET",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_field_debug_payload"
    assert data["data"]["previewOptions"] == {
        "chosenNodeId": "node-write",
        "previewType": "TARGET",
    }
    assert data["data"]["paramEntity"]["workParams"][0]["value"] == "demo"


@pytest.mark.asyncio
async def test_get_connection_info_tool_uses_dev_service(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    async def fake_get_connection_info(connection_name: str):
        assert connection_name == "demo_conn"
        return {"connectionName": connection_name, "type": "mysql"}, 200, "/webroot/decision/fdl/dev/conn/info"

    app.dev.get_connection_info = fake_get_connection_info

    _, data = await app.mcp.call_tool(
        "fdl_dev_get_connection_info",
        {"connection_name": "demo_conn"},
    )

    assert data["ok"] is True
    assert data["endpoint"] == "/webroot/decision/fdl/dev/conn/info"
    assert data["data"] == {"connectionName": "demo_conn", "type": "mysql"}


@pytest.mark.asyncio
async def test_save_work_tool_uses_dev_service(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    async def fake_save_work(payload: dict):
        assert payload == {"name": "demo"}
        return {"saved": True}, 200, "/webroot/decision/fdl/dev/work/save"

    app.dev.save_work = fake_save_work

    _, data = await app.mcp.call_tool(
        "fdl_dev_save_work",
        {"payload": {"name": "demo"}},
    )

    assert data["ok"] is True
    assert data["endpoint"] == "/webroot/decision/fdl/dev/work/save"
    assert data["data"] == {"saved": True}


@pytest.mark.asyncio
async def test_publish_work_check_tool_uses_dev_service(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    async def fake_publish_work_check(payload: dict):
        assert payload == {"name": "demo"}
        return {"check": "ok"}, 200, "/webroot/decision/fdl/dev/work/publish/check"

    app.dev.publish_work_check = fake_publish_work_check

    _, data = await app.mcp.call_tool(
        "fdl_dev_publish_work_check",
        {"payload": {"name": "demo"}},
    )

    assert data["ok"] is True
    assert data["endpoint"] == "/webroot/decision/fdl/dev/work/publish/check"
    assert data["data"] == {"check": "ok"}


@pytest.mark.asyncio
async def test_publish_work_tool_uses_dev_service(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    async def fake_publish_work(payload: dict):
        assert payload == {"name": "demo"}
        return {"published": True}, 200, "/webroot/decision/fdl/dev/work/publish"

    app.dev.publish_work = fake_publish_work

    _, data = await app.mcp.call_tool(
        "fdl_dev_publish_work",
        {"payload": {"name": "demo"}},
    )

    assert data["ok"] is True
    assert data["endpoint"] == "/webroot/decision/fdl/dev/work/publish"
    assert data["data"] == {"published": True}


@pytest.mark.asyncio
async def test_get_connection_info_tool_returns_fdl_error(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    async def fake_get_connection_info(connection_name: str):
        raise FDLError(
            code="FDL_HTTP_404",
            message="Resource not found in FDL",
            status_code=404,
            details={"endpoint": "/webroot/decision/fdl/dev/conn/info"},
        )

    app.dev.get_connection_info = fake_get_connection_info

    _, data = await app.mcp.call_tool(
        "fdl_dev_get_connection_info",
        {"connection_name": "missing_conn"},
    )

    assert data["ok"] is False
    assert data["error"]["code"] == "FDL_HTTP_404"
    assert data["error"]["details"]["endpoint"] == "/webroot/decision/fdl/dev/conn/info"


@pytest.mark.asyncio
async def test_publish_work_check_tool_returns_fdl_error(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    async def fake_publish_work_check(payload: dict):
        raise FDLError(
            code="FDL_HTTP_4XX",
            message="Client error returned by FDL",
            status_code=400,
            details={"endpoint": "/webroot/decision/fdl/dev/work/publish/check"},
        )

    app.dev.publish_work_check = fake_publish_work_check

    _, data = await app.mcp.call_tool(
        "fdl_dev_publish_work_check",
        {"payload": {"name": "demo"}},
    )

    assert data["ok"] is False
    assert data["error"]["code"] == "FDL_HTTP_4XX"
    assert data["error"]["details"]["endpoint"] == "/webroot/decision/fdl/dev/work/publish/check"


@pytest.mark.asyncio
async def test_build_workflow_template_from_dict_returns_serialized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_build_workflow_template_from_dict",
        {
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
                    "x": 120,
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
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_build_workflow_template_from_dict"
    assert data["data"]["data_flow"]["name"] == "dict-template"
    assert data["data"]["data_flow"]["lines"][0]["to_node_key"] == "python"


@pytest.mark.asyncio
async def test_validate_workflow_template_returns_normalized_template(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_validate_workflow_template",
        {
            "template": {
                "data_flow": {
                    "name": "branch-template",
                    "nodes": {
                        "branch": {
                            "node_type": "CONDITION_BRANCH",
                            "name": "条件分支",
                            "x": 0,
                            "y": 0,
                            "content": {"condition": "${count} > 0"},
                        },
                        "sql": {
                            "node_type": "SQL_SCRIPT",
                            "name": "SQL脚本",
                            "x": 120,
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
                            "x": 120,
                            "y": 120,
                            "content": {
                                "script": "print('empty')",
                                "runtime": "python",
                            },
                        },
                    },
                    "lines": [
                        {
                            "from_node_key": "branch",
                            "to_node_key": "sql",
                            "line_condition": "ON_TRUE",
                        },
                        {
                            "from_node_key": "branch",
                            "to_node_key": "python",
                            "line_condition": "ON_FALSE",
                        },
                    ],
                }
            }
        },
    )

    assert data["ok"] is True
    assert data["data"]["valid"] is True
    assert data["data"]["template"]["data_flow"]["nodes"]["branch"]["node_type"] == "CONDITION_BRANCH"


@pytest.mark.asyncio
async def test_save_workflow_template_tool_uses_generic_template_save(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    captured = {}

    async def fake_save_workflow_template(*, template: dict, work_name: str, work_id: str | None = None):
        captured["template"] = template
        captured["work_name"] = work_name
        captured["work_id"] = work_id
        return {"saved": True}, 200, "/webroot/decision/fdl/dev/work/save"

    app.dev.save_workflow_template = fake_save_workflow_template

    _, data = await app.mcp.call_tool(
        "fdl_dev_save_workflow_template",
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
            "work_name": "demo",
            "work_id": "work-1",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "/webroot/decision/fdl/dev/work/save"
    assert data["data"] == {"saved": True}
    assert captured["work_name"] == "demo"
    assert captured["work_id"] == "work-1"


@pytest.mark.asyncio
async def test_publish_workflow_template_tool_uses_generic_template_publish(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    captured = {}

    async def fake_publish_workflow_template(
        *,
        template: dict,
        work_name: str,
        work_id: str | None = None,
        describe: str = "",
        sub_work_ids: list[str] | None = None,
    ):
        captured["template"] = template
        captured["work_name"] = work_name
        captured["work_id"] = work_id
        captured["describe"] = describe
        captured["sub_work_ids"] = sub_work_ids
        return {
            "publish_result": {"published": True},
            "publish_payload": {"describe": describe, "subWorkIds": sub_work_ids or []},
        }, 200, "/webroot/decision/fdl/dev/work/publish"

    app.dev.publish_workflow_template = fake_publish_workflow_template

    _, data = await app.mcp.call_tool(
        "fdl_dev_publish_workflow_template",
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
            "work_name": "demo",
            "work_id": "work-1",
            "describe": "发布",
            "sub_work_ids": ["child-1"],
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "/webroot/decision/fdl/dev/work/publish"
    assert data["data"]["publish_result"] == {"published": True}
    assert captured["work_name"] == "demo"
    assert captured["work_id"] == "work-1"
    assert captured["describe"] == "发布"
    assert captured["sub_work_ids"] == ["child-1"]


@pytest.mark.asyncio
async def test_render_workflow_template_returns_save_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_render_workflow_template",
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
                        },
                        "python": {
                            "node_type": "PYTHON_SCRIPT",
                            "name": "Python脚本",
                            "x": 120,
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
            },
            "work_name": "demo",
            "work_id": "work-1",
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_render_workflow_template"
    assert data["data"]["workId"] == "work-1"
    assert data["data"]["workBook"]["name"] == "demo"
    assert data["data"]["workBook"]["nodes"][0]["value"]["nodes"][0]["nodeType"] == "SQL_SCRIPT"


@pytest.mark.asyncio
async def test_render_workflow_templates_batch_returns_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    _, data = await app.mcp.call_tool(
        "fdl_dev_render_workflow_templates_batch",
        {
            "items": [
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
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "local://fdl_dev_render_workflow_templates_batch"
    assert len(data["data"]["items"]) == 2
    assert data["data"]["items"][0]["save_payload"]["workId"] == "work-a"
    assert data["data"]["items"][1]["save_payload"]["workBook"]["name"] == "demo-b"


@pytest.mark.asyncio
async def test_save_workflow_templates_batch_tool_uses_batch_save(monkeypatch: pytest.MonkeyPatch) -> None:
    app = _build_app(monkeypatch)

    captured = {}

    async def fake_save_workflow_templates_batch(items: list[dict]):
        captured["items"] = items
        return [
            {
                "work_name": "demo-a",
                "work_id": "work-a",
                "save_payload": {"workId": "work-a"},
                "result": {"saved": True},
                "status_code": 200,
                "endpoint": "/webroot/decision/fdl/dev/work/save",
            }
        ], 200, "/webroot/decision/fdl/dev/work/save"

    app.dev.save_workflow_templates_batch = fake_save_workflow_templates_batch

    _, data = await app.mcp.call_tool(
        "fdl_dev_save_workflow_templates_batch",
        {
            "items": [
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
                }
            ]
        },
    )

    assert data["ok"] is True
    assert data["endpoint"] == "/webroot/decision/fdl/dev/work/save"
    assert data["data"][0]["work_name"] == "demo-a"
    assert captured["items"][0]["work_id"] == "work-a"
