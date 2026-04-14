# 数据开发能力边界计划

## 范围原则

只实现 FineDataLink `数据开发` 模块的 MCP 工具，且必须对应 FDL 已有能力。

不做：
- 运维中心
- 数据管道
- 数据服务
- 管理系统
- 回收站
- 浏览器自动化/RPA 作为交付方案
- 脱离 FDL 现有能力的自创能力

## 已确认且已接入的能力

### 1. 开发态读取
- `fdl_dev_list_connections`
- `fdl_dev_get_connection_info`
- `fdl_dev_list_connection_schemas`
- `fdl_dev_list_table_views`
- `fdl_dev_get_global_params`
- `fdl_dev_get_development_instance_info`
- `fdl_dev_list_work_versions`
- `fdl_dev_get_published_work_info`
- `fdl_dev_get_catalog_entity_info`
- `fdl_dev_get_published_instance_info`

说明：以上 endpoint 映射与请求加密模式已由测试固定，作为当前“已确认能力”基线。

### 2. 字段/预览/分区辅助
- `fdl_dev_preview_datasource`
- `fdl_dev_get_source_fields`
- `fdl_dev_get_target_fields`
- `fdl_dev_refresh_fields`
- `fdl_dev_get_field_modifies`
- `fdl_dev_get_partition_config`

### 2.5 浏览器/页面行为已确认且已工具化的能力（当前为 L2）
- `fdl_dev_get_work_development_info` → `GET /webroot/decision/fdl/dev/work/info/{workId}/development`
- `fdl_dev_list_functions` → `GET /webroot/decision/fdl/dev/function/list`
- `fdl_dev_get_downstream` → `GET /webroot/decision/fdl/plan/event/{workId}/downstream/get`

### 2.6 浏览器/页面行为已确认但尚未完全工具化的能力（L2）
- 任务目录实体创建：`POST /webroot/decision/fdl/dev/catalog/entity/create`
- 资源锁：`POST /webroot/decision/fdl/resource/try2lock`

说明：以上能力已通过页面行为/抓包确认存在，适合作为后续 MCP 能力扩展候选；但在落工具前仍应先补载荷约束与稳定性验证。

### 3. 保存/发布底座
- `fdl_dev_save_work`
- `fdl_dev_publish_work_check`
- `fdl_dev_publish_work`

### 4. 面向 agent 的本地模板能力
这些是本地 MCP 辅助层，用来表达 FDL 已存在的数据开发工作流结构，不代表新增产品能力：
- `fdl_dev_list_template_node_types`
- `fdl_dev_get_workflow_template_examples`
- `fdl_dev_build_workflow_template_from_dict`
- `fdl_dev_validate_workflow_template`
- `fdl_dev_render_workflow_template`
- `fdl_dev_save_workflow_template`
- `fdl_dev_publish_workflow_template`
- 节点级 builder：
  - `fdl_dev_build_db_read_node_template`
  - `fdl_dev_build_api_input_node_template`
  - `fdl_dev_build_db_write_node_template`
  - `fdl_dev_build_param_output_node_template`
  - `fdl_dev_build_sql_script_node_template`
  - `fdl_dev_build_python_script_node_template`
  - `fdl_dev_build_file_input_node_template`
  - `fdl_dev_build_file_output_node_template`
  - `fdl_dev_build_file_transfer_node_template`
  - `fdl_dev_build_call_task_node_template`
  - `fdl_dev_build_condition_branch_node_template`
  - `fdl_dev_build_param_assign_node_template`
  - `fdl_dev_build_merge_node_template`
- 组合模板 builder：
  - `fdl_dev_build_sql_to_python_template`
  - `fdl_dev_build_sql_python_db_template`
  - `fdl_dev_build_condition_sql_python_template`
  - `fdl_dev_build_condition_call_task_template`
  - `fdl_dev_build_condition_param_merge_template`
  - `fdl_dev_build_api_to_param_output_template`
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
- 工作流/发布辅助：
  - `fdl_dev_build_db_to_db_workflow`
  - `fdl_dev_build_publish_payload`
  - `fdl_dev_build_partition_payload`
  - `fdl_dev_build_field_debug_payload`
  - `fdl_dev_prepare_db_to_db_workflow`
  - `fdl_dev_save_db_to_db_workflow`
  - `fdl_dev_publish_db_to_db_workflow`

## 当前已编码的节点边界
仅把这些节点视为当前已确认并可供 agent 组装的能力子集：
- `DB_READ`
- `API_INPUT`
- `FILE_INPUT`
- `DB_WRITE`
- `FILE_OUTPUT`
- `FILE_TRANSFER`
- `SQL_SCRIPT`
- `PYTHON_SCRIPT`
- `CONDITION_BRANCH`
- `PARAM_ASSIGN`
- `PARAM_OUTPUT`
- `JOIN`
- `DATA_COMPARE`
- `UNION`
- `UNPIVOT`
- `JSON_PARSE`
- `ROW_FILTER`
- `FIELD_SELECT`
- `SORT`
- `AGGREGATE`
- `MERGE`
- `CALL_TASK`

说明：这只是当前确认并建模的子集，不等于整个数据开发模块的完整节点全集。

## 已确认但仍需继续梳理的能力层面
后续补工具前，应优先按“已确认 endpoint / 已确认页面动作语义 / 已确认请求载荷”三档证据补齐：
- 工作流目录/树/检索类能力
- 开发中的任务详情读取能力
- 节点详情读取/回填能力
- 保存后更多校验/检查类能力
- 发布相关的更多前置检查与结果读取能力
- 参数、变量、依赖任务、版本差异等开发常见能力

## 证据级别说明

- **L3（真实联调验证）**：在当前环境完成真实请求闭环验证（例如 save-only 实际 200 返回）。
- **L2（抓包/页面行为验证）**：已通过 HAR/页面行为确认 endpoint、头与载荷结构。
- **L1（代码推断）**：仅基于前端代码或静态线索推断，未完成请求验证。

当前仓库中关于开发态加密与写链路的结论，按 L3/L2 在**当前环境**成立；这不等于跨环境保证。若环境切换（版本、网关、安全组件）必须重新验证，尤其是加密实现可能从 `frontSeed + AES-ECB + PKCS7 + Base64` 切换到 SM4/customEncrypt。

## 实施规则
1. 新增 MCP 工具前，先确认它属于 `数据开发` 模块。
2. 必须能映射到现有 FDL 能力或已确认内部 endpoint。
3. 若只是为了让 agent 更易调用而增加本地模板工具，必须明确说明它只是 FDL 现有能力的表达层。
4. 不再把浏览器自动化当成实现方案；若使用抓包/页面行为，只能用于能力确认。
5. 先补能力边界，再补代码，不盲扩。
