# API 映射表 v1

## MCP 工具 → FDL 接口

| MCP 工具 | FDL 接口 |
|---|---|
| `fdl_execute_work_by_id` | `POST /decision/sp/client/api/fdl/workId/execute` |
| `fdl_execute_work_by_name` | `POST /decision/sp/client/api/fdl/workName/execute` |
| `fdl_get_record` | `GET /decision/sp/client/api/fdl/record/info` |
| `fdl_list_records` | `GET /decision/sp/client/api/fdl/record/list`（fallback: `/decision/sp/client/api/fdl/records/list`） |
| `fdl_terminate_records` | `POST /decision/sp/client/api/fdl/records/terminate` |
| `fdl_terminate_work` | 先查询工作流下的运行记录，再批量终止 |
| `fdl_call_data_service` | `/service/{AppId}/{ApiPath}`，auto 模式下 404 时回退到 `/service/publish/{AppId}/{ApiPath}` |
| `fdl_healthcheck` | 返回本地配置和策略状态（不发起远程请求） |

## 开发态内部 API 映射

当前 MCP 对应的开发态接口都来自 `/webroot/decision/fdl/dev/*`。

### 浏览器抓包已确认的读取/发现类接口（L2）

| 能力 | HTTP | Endpoint | 说明 |
|---|---|---|---|
| 任务目录新建实体 | `POST` | `/webroot/decision/fdl/dev/catalog/entity/create` | 已抓到真实请求与响应，响应返回 `id/name/type/publishState/editable` |
| 任务目录实体信息 | `GET` | `/webroot/decision/fdl/dev/catalog/entity/info` | 已抓到 `workId` 查询，返回路径、创建人、发布状态等 |
| 开发态任务定义读取 | `GET` | `/webroot/decision/fdl/dev/work/info/{workId}/development` | 页面进入设计器时会读取；当前环境确认其属于开发态核心读接口 |
| 开发态实例信息 | `GET` | `/webroot/decision/fdl/dev/instance/{workId}/development/info/get` | 已抓到真实返回，当前样例返回 `{log: null, statistic: []}` |
| 表达式函数列表 | `GET` | `/webroot/decision/fdl/dev/function/list` | 已抓到真实返回，包含 `BASE64/MD5/SHA/UUID/CONCAT/SUBSTR/to_json` 等 |
| 全局参数查询 | `GET` | `/webroot/decision/fdl/dev/param/global/query` | 已抓到真实返回；当前样例 `data=[]` |
| 下游关系查询 | `GET` | `/webroot/decision/fdl/plan/event/{workId}/downstream/get` | 已在页面网络请求中确认存在，用于任务关系/影响范围类信息 |
| 资源加锁尝试 | `POST` | `/webroot/decision/fdl/resource/try2lock` | 已在页面网络请求中确认存在，用于编辑前资源锁定协同 |

### 字段/预览类接口（页面联动已确认）

| 能力 | HTTP | Endpoint | 说明 |
|---|---|---|---|
| 数据预览 | `POST` | `/webroot/decision/fdl/dev/datasource/preview` | 节点配置面板中预览数据时触发 |
| 源字段获取 | `POST` | `/webroot/decision/fdl/dev/datasource/field/source` | 节点选择输入源/上游后触发 |
| 目标字段获取 | `POST` | `/webroot/decision/fdl/dev/datasource/field/target` | 输出/写入类节点配置目标字段时触发 |
| 字段刷新 | `POST` | `/webroot/decision/fdl/dev/datasource/field/refresh` | 已由仓库实现与测试固定 |
| 字段修改信息 | `POST` | `/webroot/decision/fdl/dev/datasource/field/modifies` | 已由仓库实现与测试固定 |
| 分区配置获取 | `POST` | `/webroot/decision/fdl/dev/conn/table/conf/partition/get` | 已由仓库实现与测试固定 |

### 写链路（save / publish-check / publish）

| MCP 工具 | HTTP | Endpoint | Payload 结构 |
|---|---|---|---|
| `fdl_dev_save_work(payload)` | `POST` | `/webroot/decision/fdl/dev/work/save` | 直接提交 `save payload`（`workId/workBook/...`） |
| `fdl_dev_publish_work_check(payload)` | `POST` | `/webroot/decision/fdl/dev/work/publish/check` | 与 save 同结构（同一份 `save payload`） |
| `fdl_dev_publish_work(payload)` | `POST` | `/webroot/decision/fdl/dev/work/publish` | `{"dataDevWork": <save payload>, "subWorkIds": [], "describe": ""}` |

### 相关本地辅助工具映射

| MCP 工具 | 作用 |
|---|---|
| `fdl_dev_build_db_read_node_template(datasource_type, connection_name, sql, ...)` | 构造 `DB_READ` 单节点结构，用于数据库读取节点建模与字典拼装 |
| `fdl_dev_build_api_input_node_template(url, method, ...)` | 构造 `API_INPUT` 单节点结构，用于 API 输入节点建模与字典拼装 |
| `fdl_dev_build_db_write_node_template(datasource_type, connection_name, schema, table, ...)` | 构造 `DB_WRITE` 单节点结构，用于目标库写入节点建模与字典拼装 |
| `fdl_dev_build_param_output_node_template(outputs, ...)` | 构造 `PARAM_OUTPUT` 单节点结构，用于参数输出节点建模与字典拼装 |
| `fdl_dev_build_sql_script_node_template(sql, ...)` | 构造 `SQL_SCRIPT` 单节点结构，用于 SQL 脚本节点建模与字典拼装 |
| `fdl_dev_build_python_script_node_template(script, ...)` | 构造 `PYTHON_SCRIPT` 单节点结构，用于 Python 脚本节点建模与字典拼装 |
| `fdl_dev_build_file_input_node_template(path, file_format, ...)` | 构造 `FILE_INPUT` 单节点结构，用于文件输入节点建模与字典拼装 |
| `fdl_dev_build_file_output_node_template(path, file_format, ...)` | 构造 `FILE_OUTPUT` 单节点结构，用于文件输出节点建模与字典拼装 |
| `fdl_dev_build_file_transfer_node_template(source_path, target_path, ...)` | 构造 `FILE_TRANSFER` 单节点结构，用于文件传输节点建模与字典拼装 |
| `fdl_dev_build_call_task_node_template(called_work_id, called_work_name, ...)` | 构造 `CALL_TASK` 单节点结构，用于任务调用节点建模与字典拼装 |
| `fdl_dev_build_condition_branch_node_template(condition, ...)` | 构造 `CONDITION_BRANCH` 单节点结构，用于条件分支节点建模与字典拼装 |
| `fdl_dev_build_param_assign_node_template(assignments, ...)` | 构造 `PARAM_ASSIGN` 单节点结构，用于参数赋值节点建模与字典拼装 |
| `fdl_dev_build_merge_node_template(...)` | 构造 `MERGE` 单节点结构，用于分支汇聚节点建模与字典拼装 |
| `fdl_dev_build_publish_payload(save_payload, describe, sub_work_ids)` | 将 save payload 包装为 publish 所需 `dataDevWork/subWorkIds/describe` 结构 |
| `fdl_dev_build_api_to_param_output_template(api_url, output_fields, ...)` | 构造 `API_INPUT -> PARAM_OUTPUT` 两节点模板，用于 API 输入到参数输出场景 |
| `fdl_dev_build_row_filter_template(source_sql, condition, ...)` | 构造 `SQL_SCRIPT -> ROW_FILTER` 模板，用于行过滤场景 |
| `fdl_dev_build_field_select_template(source_sql, selected_fields, ...)` | 构造 `SQL_SCRIPT -> FIELD_SELECT` 模板，用于字段选择/映射场景 |
| `fdl_dev_build_sort_template(source_sql, sort_fields, ...)` | 构造 `SQL_SCRIPT -> SORT` 模板，用于排序场景 |
| `fdl_dev_build_aggregate_template(source_sql, aggregations, group_fields, ...)` | 构造 `SQL_SCRIPT -> AGGREGATE` 模板，用于分组聚合场景 |
| `fdl_dev_build_file_to_db_template(file_path, file_format, target_connection_name, ...)` | 构造 `FILE_INPUT -> DB_WRITE` 模板，用于文件导入到数据库场景 |
| `fdl_dev_build_db_to_file_template(source_sql, target_path, target_file_format, ...)` | 构造 `DB_READ -> FILE_OUTPUT` 模板，用于数据库导出到文件场景 |
| `fdl_dev_build_file_transfer_template(source_path, target_path, ...)` | 构造 `FILE_TRANSFER` 模板，用于文件复制/移动场景 |
| `fdl_dev_render_workflow_templates_batch(items)` | 批量渲染多个模板条目为 save payload 列表，不发起远端请求 |
| `fdl_dev_save_workflow_templates_batch(items)` | 逐项渲染模板并顺序调用 `/work/save`，返回每项 save-only 汇总结果 |
| `fdl_dev_save_db_to_db_workflow(...)` | 本地构造 DB→DB save payload 后调用 `/work/save` |
| `fdl_dev_publish_db_to_db_workflow(...)` | 本地构造后按 `/work/save` → `/work/publish/check` → `/work/publish` 编排 |

## 会话 / 鉴权 / 加密备注

- 开发态页面请求在当前环境下依赖已登录会话；实现侧需同时关注：`Authorization: Bearer <token>`、`fine_auth_token`、`JSESSIONID`、`tenantId`。
- 已确认存在 `POST /webroot/decision/token/refresh` 刷新链路，页面会在会话续期时调用。
- 当前环境中，开发态写请求与部分读请求存在 `fdl-encrypt: plaintext` / `fdl-encrypt: encrypted` 分流；不能假定所有 `/fdl/dev/*` 都是明文。
- 当响应头出现 `alreadyencrypted: true` 时，客户端需要按当前环境加密方案解密后再交给上层。
- 当前仓库关于开发态加密的已知有效结论，仍限定在**当前环境**；跨环境需重新验证。

## 错误码前缀

| 前缀 | 含义 |
|---|---|
| `FDL_AUTH_*` | 认证/鉴权失败 |
| `FDL_HTTP_*` | HTTP 层错误 |
| `FDL_TASK_*` | 任务服务层错误 |
| `FDL_POLICY_*` | 策略拦截（白名单、限流） |
