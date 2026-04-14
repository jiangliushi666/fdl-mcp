# fdl-mcp

`fdl-mcp` 是一个面向 FineDataLink 的 MCP Server，目标是把 FDL 的任务执行能力和数据开发接口封装成可被 Agent 直接调用的工具集。

> 状态说明
>
> 这是一个半成品项目，目前更接近“可运行的实验性原型”而不是生产级成品。它已经覆盖一部分真实可用的 FineDataLink 任务执行与数据开发能力，但接口覆盖、环境兼容性、异常处理、文档完整度和稳定性都还在持续补齐。

它覆盖两类能力：

- 官方任务侧 API：按 `workId` 或 `workName` 执行工作流、查询记录、终止执行、调用数据服务。
- 数据开发侧 API：读取连接和任务开发信息，构造工作流模板，执行保存、发布检查和发布。

项目当前以 FineDataLink `数据开发` 模块为主，浏览器自动化只用于环境确认和会话提取，不作为交付形态。

## 主要能力

### 1. 官方任务工具

- `fdl_execute_work_by_id`
- `fdl_execute_work_by_name`
- `fdl_get_record`
- `fdl_list_records`
- `fdl_terminate_records`
- `fdl_terminate_work`
- `fdl_call_data_service`
- `fdl_healthcheck`

### 2. 数据开发读取工具

- `fdl_dev_list_connections`
- `fdl_dev_get_connection_info`
- `fdl_dev_list_connection_schemas`
- `fdl_dev_list_table_views`
- `fdl_dev_get_global_params`
- `fdl_dev_get_development_instance_info`
- `fdl_dev_get_catalog_entity_info`
- `fdl_dev_get_work_development_info`
- `fdl_dev_list_work_versions`
- `fdl_dev_get_published_work_info`
- `fdl_dev_get_published_instance_info`
- `fdl_dev_list_functions`
- `fdl_dev_get_downstream`

### 3. 数据开发字段与调试工具

- `fdl_dev_preview_datasource`
- `fdl_dev_get_source_fields`
- `fdl_dev_get_target_fields`
- `fdl_dev_refresh_fields`
- `fdl_dev_get_field_modifies`
- `fdl_dev_get_partition_config`

### 4. 工作流模板与高层封装

- `fdl_dev_list_template_node_types`
- `fdl_dev_get_workflow_template_examples`
- `fdl_dev_render_workflow_templates_batch`
- `fdl_dev_save_workflow_templates_batch`
- `fdl_dev_build_db_to_db_workflow`
- `fdl_dev_prepare_db_to_db_workflow`
- `fdl_dev_save_db_to_db_workflow`
- `fdl_dev_publish_db_to_db_workflow`
- `fdl_dev_build_publish_payload`
- `fdl_dev_build_partition_payload`
- `fdl_dev_build_field_debug_payload`

### 5. 底层保存与发布能力

- `fdl_dev_save_work`
- `fdl_dev_publish_work_check`
- `fdl_dev_publish_work`

### 6. Chrome 已登录会话接管

- `fdl_dev_configure_chrome_session`

这个工具用于把浏览器当前页面的 `base_url`、`fine_auth_token`、Cookie 和 `Dec.system.frontSeed` 注入运行时配置，适合开发态接口调试。

## 当前实现特点

- Python 3.11+
- 基于 `mcp` 的 `FastMCP`
- HTTP 客户端使用 `httpx`
- 支持 `aksk`、`appcode`、`fine_auth_token`、`none` 四种认证模式
- 支持 `auto | new | legacy` 三种服务路径解析策略
- 支持开发态写链路的 AES 加解密
- 内置白名单、限流、审计日志和幂等缓存

## 安装

建议使用 `uv`。

```powershell
cd C:\Users\j\Desktop\fdl-mcp
uv sync --extra dev
```

如果只想直接运行，也可以：

```powershell
cd C:\Users\j\Desktop\fdl-mcp
uv run --python 3.11 --with ".[dev]" -m fdl_mcp.server
```

## 配置

项目从环境变量读取配置，核心字段如下。

| 变量 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `FDL_BASE_URL` | 是 | - | FDL 服务根地址 |
| `FDL_AUTH_MODE` | 否 | `aksk` | `aksk` \| `appcode` \| `fine_auth_token` \| `none` |
| `FDL_CLIENT_ID` | 按模式 | - | `aksk` 模式必填 |
| `FDL_SECRET` | 按模式 | - | `aksk` 模式必填 |
| `FDL_APPCODE` | 按模式 | - | `appcode` 模式必填 |
| `FDL_FINE_AUTH_TOKEN` | 按模式 | - | `fine_auth_token` 模式必填 |
| `FDL_FINE_AUTH_COOKIE` | 否 | - | 可选，若未显式传 token，会尝试从 Cookie 中提取 |
| `FDL_TIMEOUT_MS` | 否 | `10000` | 请求超时 |
| `FDL_RETRY_MAX` | 否 | `2` | 最大重试次数 |
| `FDL_SERVICE_PATH_MODE` | 否 | `auto` | 服务路径模式 |
| `FDL_ENCRYPT_MODE` | 否 | `none` | `none` \| `aes` |
| `FDL_ENCRYPT_KEY` | 按模式 | - | `aes` 模式必填 |
| `FDL_ALLOWED_WORK_IDS` | 否 | 空 | 允许访问的工作流 ID 白名单 |
| `FDL_ALLOWED_WORK_NAMES` | 否 | 空 | 允许访问的工作流名称白名单 |
| `FDL_ALLOWED_TOOLS` | 否 | 空 | 工具白名单 |
| `FDL_RATE_LIMIT_PER_MIN` | 否 | `120` | 每调用方每工具每分钟限流 |
| `FDL_IDEMPOTENCY_TTL_SEC` | 否 | `600` | 幂等缓存 TTL |

可从 `.env.example` 开始：

```powershell
Copy-Item .env.example .env
```

### 示例 1：AK/SK 模式

```powershell
$env:FDL_BASE_URL='https://your-fdl-host'
$env:FDL_AUTH_MODE='aksk'
$env:FDL_CLIENT_ID='your-client-id'
$env:FDL_SECRET='your-secret'
```

### 示例 2：浏览器登录态 + AES 写链路

```powershell
$env:FDL_BASE_URL='https://your-fdl-host'
$env:FDL_AUTH_MODE='fine_auth_token'
$env:FDL_FINE_AUTH_TOKEN='your-token'
$env:FDL_FINE_AUTH_COOKIE='fine_auth_token=your-token'
$env:FDL_ENCRYPT_MODE='aes'
$env:FDL_ENCRYPT_KEY='1ED6F5BA8CFD75F8'
```

## 启动

```powershell
cd C:\Users\j\Desktop\fdl-mcp
uv run -m fdl_mcp.server
```

服务入口位于 `src/fdl_mcp/server.py`。

## 开发态写链路说明

这个项目已经内置开发态写接口的加密和解密能力，适用于：

- `fdl_dev_save_work`
- `fdl_dev_publish_work_check`
- `fdl_dev_publish_work`

当前代码约定如下：

- 当 `FDL_ENCRYPT_MODE=aes` 时，提交前会使用 `FDL_ENCRYPT_KEY` 对请求体加密。
- 当响应头包含 `alreadyencrypted: true` 时，会自动解密返回值。
- 明文 JSON 会直接解析为对象返回，非 JSON 明文会以 `raw` 字段返回。

`FDL_ENCRYPT_KEY` 通常来自页面中的 `Dec.system.frontSeed`。

## 推荐使用流程

### 只读探索

1. `fdl_healthcheck`
2. `fdl_dev_list_connections`
3. `fdl_dev_get_connection_info`
4. `fdl_dev_get_work_development_info`
5. `fdl_dev_get_downstream`

### 构造并保存 DB -> DB 工作流

1. `fdl_dev_prepare_db_to_db_workflow`
2. 检查返回的字段、分区、目标表配置
3. `fdl_dev_save_db_to_db_workflow`
4. 如需发布，再调用 `fdl_dev_publish_db_to_db_workflow`

### 直接操作底层 payload

1. 用 `fdl_dev_build_*` 系列工具构造节点或 save payload
2. 必要时通过 `fdl_dev_build_publish_payload` 包装
3. 调用 `fdl_dev_save_work` / `fdl_dev_publish_work_check` / `fdl_dev_publish_work`

## 项目结构

```text
fdl-mcp/
├─ src/fdl_mcp/
│  ├─ server.py               # MCP 入口与工具注册
│  ├─ client.py               # HTTP 调用封装
│  ├─ auth.py                 # 认证头构造
│  ├─ config.py               # 环境变量与配置校验
│  ├─ services.py             # 官方任务服务
│  ├─ dev_services.py         # 数据开发服务与模板构造
│  ├─ endpoint_resolver.py    # 新旧路径兼容
│  ├─ policy.py               # 白名单与限流
│  ├─ idempotency.py          # 幂等缓存
│  ├─ audit.py                # 审计日志
│  └─ redaction.py            # 敏感信息脱敏
├─ tests/                     # 单元测试
├─ docs/                      # 调研、边界与运维文档
└─ pyproject.toml
```

## 测试

```powershell
cd C:\Users\j\Desktop\fdl-mcp
uv run pytest
```

如果只跑核心测试：

```powershell
uv run pytest tests/test_config.py tests/test_server.py tests/test_dev_services.py
```

## 文档

- `docs/api-mapping.md`
- `docs/dev-capability-boundary.md`
- `docs/dev-node-capability-matrix.md`
- `docs/handoff.md`
- `docs/runbook.md`
- `docs/security.md`
- `docs/investigation-summary.md`

## 当前边界

- 这是一个半成品仓库，适合调研、二次开发和受控环境验证，不应直接视为生产就绪方案。
- 项目聚焦 FineDataLink `数据开发` 与任务执行，不覆盖整个平台所有模块。
- 浏览器自动化仅作为会话提取和接口确认手段，不应作为最终集成方案。
- 开发态接口是否需要加密、请求头细节、字段语义，可能随环境变化，跨环境必须重新验证。
- 高层 builder 已能覆盖部分典型节点组合，但并不等于完整覆盖设计器全部节点类型。

## 注意事项

- 不要把真实 `fine_auth_token`、Cookie、AK/SK、`frontSeed` 提交到仓库。
- `.env` 应只保留在本地。
- 若要把项目接入其他 Agent，建议优先开放只读工具，再逐步开放保存和发布工具。

## 许可证

本项目使用 MIT License，详见 `LICENSE`。
