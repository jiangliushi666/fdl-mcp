# fdl-mcp

FineDataLink MCP 服务端，用于任务全生命周期管理：

- 通过 `workId` 或 `workName` 执行工作流
- 查询执行记录
- 终止记录或工作流目标
- 调用数据服务接口（兼容新旧路径版本）

## 快速开始

1. 安装依赖并启动：

```powershell
$env:UV_CACHE_DIR='C:/Users/j/Desktop/.uv-cache'
cd C:\Users\j\Desktop\fdl-mcp
uv run --python 3.11 --with ".[dev]" -m fdl_mcp.server
```

2. 配置环境变量：

```powershell
$env:FDL_BASE_URL='https://your-fdl-host'
$env:FDL_AUTH_MODE='aksk'          # aksk | appcode | fine_auth_token
$env:FDL_CLIENT_ID='your-client-id'
$env:FDL_SECRET='your-secret'
$env:FDL_TIMEOUT_MS='10000'
$env:FDL_RETRY_MAX='2'
```

3. 可选安全策略：

```powershell
$env:FDL_ALLOWED_WORK_IDS='1001,1002'
$env:FDL_ALLOWED_WORK_NAMES='daily_sync,weekly_etl'
$env:FDL_RATE_LIMIT_PER_MIN='120'
```

## 工具列表

- `fdl_execute_work_by_id(work_id, payload?, idempotency_key?)`
- `fdl_execute_work_by_name(work_name, payload?, idempotency_key?)`
- `fdl_get_record(record_id)`
- `fdl_list_records(work_id?, work_name?, status?, time_from?, time_to?, page?, page_size?)`
- `fdl_terminate_records(record_ids[])`
- `fdl_terminate_work(work_id?, work_name?)`
- `fdl_call_data_service(app_id, api_path, method, query?, headers?, body?)`
- `fdl_healthcheck()`

## 环境变量说明

| 变量 | 默认值 | 说明 |
|---|---|---|
| `FDL_BASE_URL` | （必填） | FDL 服务地址 |
| `FDL_AUTH_MODE` | `aksk` | `aksk` \| `appcode` \| `fine_auth_token` |
| `FDL_CLIENT_ID` | — | aksk 模式必填 |
| `FDL_SECRET` | — | aksk 模式必填 |
| `FDL_APPCODE` | — | appcode 模式必填 |
| `FDL_FINE_AUTH_TOKEN` | — | fine_auth_token 模式必填 |
| `FDL_TIMEOUT_MS` | `10000` | 单次请求超时（毫秒） |
| `FDL_RETRY_MAX` | `2` | 瞬态错误最大重试次数 |
| `FDL_SERVICE_PATH_MODE` | `auto` | `auto` \| `new` \| `legacy` |
| `FDL_ALLOWED_WORK_IDS` | （空=不限） | 逗号分隔的工作流 ID 白名单 |
| `FDL_ALLOWED_WORK_NAMES` | （空=不限） | 逗号分隔的工作流名称白名单 |
| `FDL_ALLOWED_TOOLS` | （空=不限） | 逗号分隔的工具白名单 |
| `FDL_RATE_LIMIT_PER_MIN` | `120` | 每调用方/工具每分钟限流（进程内） |
| `FDL_IDEMPOTENCY_TTL_SEC` | `600` | 幂等键 TTL（秒，内存存储） |

## 文档

- [API 映射表](docs/api-mapping.md)
- [安全模型](docs/security.md)
- [运维手册](docs/runbook.md)
