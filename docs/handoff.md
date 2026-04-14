# Handoff (for next agent)

## 1) Hard constraints (must not break)
- Scope is strictly FineDataLink **数据开发** module.
- During test/live validation, stay **save-only**.
- Do **not** call publish/check/schedule tools in this stage.
- Before any live call, enable `FDL_ALLOWED_TOOLS` guardrail.

Recommended whitelist for current phase:
- `fdl_dev_configure_chrome_session`
- `fdl_dev_save_work`

## 2) Current status snapshot
- Phase 1 is complete and live save-only validated:
  - `API_INPUT`
  - `PARAM_OUTPUT`
- Phase 2 template-assembly tooling is implemented and live save-only validated:
  - `JOIN`
  - `DATA_COMPARE`
  - `UNION`
  - `UNPIVOT`
  - `JSON_PARSE`
  - `ROW_FILTER`
  - `FIELD_SELECT`
  - `SORT`
  - `AGGREGATE`
- Phase 3 local modeling is implemented and live save-only validated:
  - sync mode parameterization for `DB_WRITE`
  - `FILE_INPUT`
  - `FILE_OUTPUT`
  - `FILE_TRANSFER`
  - `FILE_INPUT -> DB_WRITE`
  - `DB_READ -> FILE_OUTPUT`
  - `FILE_TRANSFER` single-node flow
- Phase 4 batch helpers are implemented and tested locally:
  - `render_workflow_templates_batch(...)`
  - `save_workflow_templates_batch(...)`
  - `fdl_dev_render_workflow_templates_batch`
  - `fdl_dev_save_workflow_templates_batch`
- Remaining gap: batch helpers do not yet have dedicated L3 batch-run evidence; per-flow L3 save-only evidence is complete.

## 2.5) Browser/API discovery evidence for future MCP expansion
- Confirmed via live page/network inspection (`L2`):
  - `POST /webroot/decision/fdl/dev/catalog/entity/create`
  - `GET /webroot/decision/fdl/dev/catalog/entity/info?workId=...`
  - `GET /webroot/decision/fdl/dev/work/info/{workId}/development`
  - `GET /webroot/decision/fdl/dev/function/list`
  - `GET /webroot/decision/fdl/plan/event/{workId}/downstream/get`
  - `POST /webroot/decision/fdl/resource/try2lock`
- Newly modeled as MCP tools from existing L2 evidence:
  - `fdl_dev_get_work_development_info`
  - `fdl_dev_list_functions`
  - `fdl_dev_get_downstream`
- Confirmed page structure relevant to agent modeling:
  - 数据开发 designer contains nested 数据转换 sub-designer.
  - Nodes support graph connections/ports/edges; capability inventory must include topology, not just node names.
  - Node config surfaces were directly inspected for `DB表输入`, `DB表输出`, `JSON解析`, `字段设置`, `分组汇总`, `Spark SQL`, `Python`.
- Important current interpretation:
  - `Spark SQL` page existence is confirmed in UI, but payload semantics are not yet modeled in repo.
  - `Python` / `SQL` pages are confirmed in UI, but whether they are exactly equivalent to current `PYTHON_SCRIPT` / `SQL_SCRIPT` builders still needs payload-level confirmation.

## 3) What was completed in code
### DevService template builders (Phase 2 / Phase 3 / Phase 4)
- `src/fdl_mcp/dev_services.py`
  - `build_join_template(...)`
  - `build_data_compare_template(...)`
  - `build_union_template(...)`
  - `build_unpivot_template(...)`
  - `build_json_parse_template(...)`
  - `build_row_filter_template(...)`
  - `build_field_select_template(...)`
  - `build_sort_template(...)`
  - `build_aggregate_template(...)`
  - `build_sync_mode_config(...)`
  - `build_file_input_node_template(...)`
  - `build_file_output_node_template(...)`
  - `build_file_transfer_node_template(...)`
  - `build_file_to_db_template(...)`
  - `build_db_to_file_template(...)`
  - `build_file_transfer_template(...)`
  - `render_workflow_templates_batch(...)`
  - `save_workflow_templates_batch(...)`

### MCP tools exposed in server
- `src/fdl_mcp/server.py`
  - `fdl_dev_get_work_development_info`
  - `fdl_dev_list_functions`
  - `fdl_dev_get_downstream`
  - `fdl_dev_build_join_template`
  - `fdl_dev_build_data_compare_template`
  - `fdl_dev_build_union_template`
  - `fdl_dev_build_unpivot_template`
  - `fdl_dev_build_json_parse_template`
  - `fdl_dev_build_row_filter_template`
  - `fdl_dev_build_field_select_template`
  - `fdl_dev_build_sort_template`
  - `fdl_dev_build_aggregate_template`
  - `fdl_dev_build_file_to_db_template`
  - `fdl_dev_build_db_to_file_template`
  - `fdl_dev_build_file_transfer_template`
  - `fdl_dev_render_workflow_templates_batch`
  - `fdl_dev_save_workflow_templates_batch`

### Example catalog expanded
- `fdl_dev_get_workflow_template_examples` now includes:
  - `join_flow`
  - `data_compare_flow`
  - `union_flow`
  - `unpivot_flow`
  - `json_parse_flow`
  - `row_filter_flow`
  - `field_select_flow`
  - `sort_flow`
  - `aggregate_flow`
  - `file_to_db_flow`
  - `db_to_file_flow`
  - `file_transfer_flow`

## 4) Test status (latest)
- `uv run --python 3.11 --with ".[dev]" -m pytest tests/test_dev_services.py` → `78 passed`
- `uv run --python 3.11 --with ".[dev]" -m pytest tests/test_server.py` → `54 passed`
- `uv run --python 3.11 --with ".[dev]" -m pytest tests/test_dev_services.py tests/test_server.py` → `132 passed`
- `uv run --python 3.11 --with ".[dev]" -m pytest` → `132 passed` (last known local status before next live save-only validation round)

## 5) Existing live save-only evidence
### Baseline save-only (already done)
- time: `2026-03-07T03:40:59.373432+00:00`
- work_id: `49d18c3f-e92e-48b7-bb1c-069d79a4070b`
- endpoint: `/webroot/decision/fdl/dev/work/save`
- HTTP: `200`
- trace_id: `38f4c95d32e64defa121a83d1f9c14c0`

### Phase 1 API_INPUT→PARAM_OUTPUT save-only (already done)
- time: `2026-03-07T06:29:36.187391+00:00`
- work_id: `49d18c3f-e92e-48b7-bb1c-069d79a4070b`
- endpoint: `/webroot/decision/fdl/dev/work/save`
- HTTP: `200`
- trace_id: `92f4e0e4730c4eefaa6ca32f2af2505c`
- business result: `code=200`, `error=false`, `data=success`

### Phase 2 / Phase 3 save-only validation round (2026-03-07)
- target task: `claude`
- work_id: `f746a9ee-0a4d-4b1e-8738-f4511c459111`
- endpoint: `/webroot/decision/fdl/dev/work/save`
- HTTP: all `200`
- business result: all `code=200`, `error=false`, `data=success`
- records:
  - `JOIN` → `trace_id=53c282d155864dc6b02e11e85955cc21`
  - `DATA_COMPARE` → `trace_id=344d7e4c785247b1a8ffe80fed1ce9c9`
  - `UNION` → `trace_id=f4f60dcf1fc84dc28c6202a5f9f22393`
  - `UNPIVOT` → `trace_id=3bba2e5f351b4e8c98feac9ce4e6d426`
  - `JSON_PARSE` → `trace_id=556da3d90f8540b69fcf8cf7e094bd69`
  - `ROW_FILTER` → `trace_id=bf0ce504af424ca79c1b3668b0f40e4c`
  - `FIELD_SELECT` → `trace_id=a4c6f422c29c468fb63320c486040302`
  - `SORT` → `trace_id=796fd97d932e43fba2765d19cd7eb29d`
  - `AGGREGATE` → `trace_id=3f55617ed50441b9ac380ae6c84eb887`
  - `FILE_INPUT->DB_WRITE` → `trace_id=1904a19a116a4d3a9311ced8d8fb3eab`
  - `DB_READ->FILE_OUTPUT` → `trace_id=77028e52940649e88b752a9c8531d758`
  - `FILE_TRANSFER` → `trace_id=dded8879626a4c9ea01c8d1e4345ff56`

## 6) 本地测试环境验证（2026-03-09）

### 测试环境信息
- **FDL 地址**: http://192.168.138.35:8068
- **账号**: fdlxm / 2383566697x
- **认证模式**: fine_auth_token (从浏览器自动提取)
- **加密模式**: aes (frontSeed: 1ED6F5BA8CFD75F8)

### 连接测试结果
- ✓ 配置加载成功
- ✓ 客户端创建成功
- ✓ 认证通过 (fine_auth_token)
- ✓ 加密/解密正常 (AES-ECB)
- ✓ 读取接口测试通过:
  - `get_global_params`: HTTP 200, Business Code 200, 返回 0 个全局参数
  - `list_connections`: HTTP 200, Business Code 200, 返回 18 个 MySQL 连接
  - `list_functions`: HTTP 200, Business Code 200, 返回 35 个函数

### 核心问题发现

#### ✗ 生成的任务无法打开
- **现象**:
  - `build_db_to_db_workflow` 生成 payload
  - `save_work` 返回 HTTP 200 + Business Code 200 (成功)
  - 但在 FDL 界面中打开任务时，页面空白
- **测试任务**: Work ID `8b0cfeb3-e6d2-4e9e-b9d5-ec3092ef0dc4` (claude-1/claude-1.1)
- **已排查**:
  - ✓ Payload 顶层结构正确
  - ✓ workBook 结构正确
  - ✓ DATA_FLOW 节点类型正确
  - ✗ nodeContent 详细配置可能有问题

#### ✗ 缺少创建功能
- 没有创建文件夹的 API
- 没有创建任务实体的 API
- 必须手动创建任务实体后才能用 fdl-mcp 配置

### 已创建的文档和文件
- `docs/HANDOVER.md`: **完整交接文档（重要）**
- `docs/test-issues.md`: 详细问题记录
- `docs/test-environment.md`: 测试环境配置指南
- `docs/investigation-summary.md`: 调查结果总结
- `working_task_payload.json`: 真实任务 payload (API_INPUT->PARAM_OUTPUT)
- `fdl_mcp_payload.json`: fdl-mcp 生成的 payload (DB_READ->DB_WRITE)
- 多个测试脚本: `test_*.py`, `compare_payloads.py`, `read_working_task.py`

### 当前状态
- 项目已成功连接到本地 FDL 实例
- 基础读取功能验证通过
- **核心问题**: 生成的任务无法打开，需要对比真实的 DB->DB 任务找出差异
- **下一步**: 见 `docs/HANDOVER.md` 中的详细行动计划

## 7) Next agent checklist (execute in order)
1. Keep guardrail strictly enabled:
   - `FDL_ALLOWED_TOOLS=fdl_dev_configure_chrome_session,fdl_dev_save_work,fdl_dev_get_global_params,fdl_dev_list_connections,fdl_dev_get_development_instance_info,fdl_dev_list_functions,fdl_dev_get_downstream,fdl_dev_get_catalog_entity_info`
2. 测试 save-only 功能:
   - 从界面获取一个测试任务的 work_id (例如 "DEMO示例/claude")
   - 使用 `fdl_dev_get_development_instance_info` 读取任务配置
   - 使用 `fdl_dev_save_work` 保存（不修改配置）
   - 验证返回 HTTP 200 + Business Code 200
3. If batch helper L3 evidence is needed, use:
   - `fdl_dev_render_workflow_templates_batch`
   - `fdl_dev_save_workflow_templates_batch`
   - still save-only; do not call publish/check/schedule.
4. For any new save-only run, record in this file:
   - timestamp
   - work_id
   - endpoint
   - HTTP status
   - trace_id
   - business `code/error/data`
5. Keep `docs/dev-node-capability-matrix.md` aligned with evidence level.

## 7) Update rules for docs
- If Phase 2 live save-only passes, update:
  - `docs/dev-node-capability-matrix.md` (L1/in_progress → L3/done where applicable)
  - this `docs/handoff.md` with traceable records.
- Keep entries concise and evidence-based. Do not add speculative cross-environment claims.

## 8) Key files
- `src/fdl_mcp/dev_services.py`
- `src/fdl_mcp/server.py`
- `tests/test_dev_services.py`
- `tests/test_server.py`
- `docs/dev-node-capability-matrix.md`
- `docs/dev-capability-boundary.md`
- `docs/handoff.md`
