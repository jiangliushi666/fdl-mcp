# fdl-mcp

FineDataLink MCP server for task lifecycle operations:

- execute workflow by `workId` or `workName`
- query records
- terminate records or workflow targets
- call data service endpoints with version-compatible routing

## Quick Start

1. Install dependencies and run:

```powershell
$env:UV_CACHE_DIR='C:/Users/j/Desktop/.uv-cache'
cd C:\Users\j\Desktop\fdl-mcp
uv run --python 3.11 --with ".[dev]" -m fdl_mcp.server
```

2. Configure environment variables:

```powershell
$env:FDL_BASE_URL='https://your-fdl-host'
$env:FDL_AUTH_MODE='aksk'          # aksk | appcode | fine_auth_token
$env:FDL_CLIENT_ID='your-client-id'
$env:FDL_SECRET='your-secret'
$env:FDL_TIMEOUT_MS='10000'
$env:FDL_RETRY_MAX='2'
```

3. Optional policy hardening:

```powershell
$env:FDL_ALLOWED_WORK_IDS='1001,1002'
$env:FDL_ALLOWED_WORK_NAMES='daily_sync,weekly_etl'
$env:FDL_RATE_LIMIT_PER_MIN='120'
```

## Tool List

- `fdl_execute_work_by_id(work_id, payload?, idempotency_key?)`
- `fdl_execute_work_by_name(work_name, payload?, idempotency_key?)`
- `fdl_get_record(record_id)`
- `fdl_list_records(work_id?, work_name?, status?, time_from?, time_to?, page?, page_size?)`
- `fdl_terminate_records(record_ids[])`
- `fdl_terminate_work(work_id?, work_name?)`
- `fdl_call_data_service(app_id, api_path, method, query?, headers?, body?)`
- `fdl_healthcheck()`

## Environment Variables

- `FDL_BASE_URL` (required)
- `FDL_AUTH_MODE` = `aksk|appcode|fine_auth_token` (default: `aksk`)
- `FDL_CLIENT_ID`
- `FDL_SECRET`
- `FDL_APPCODE`
- `FDL_FINE_AUTH_TOKEN`
- `FDL_TIMEOUT_MS` (default: `10000`)
- `FDL_RETRY_MAX` (default: `2`)
- `FDL_SERVICE_PATH_MODE` = `auto|new|legacy` (default: `auto`)
- `FDL_ALLOWED_WORK_IDS` (comma separated)
- `FDL_ALLOWED_WORK_NAMES` (comma separated)
- `FDL_ALLOWED_TOOLS` (comma separated)
- `FDL_RATE_LIMIT_PER_MIN` (default: `120`)
- `FDL_IDEMPOTENCY_TTL_SEC` (default: `600`)

## Docs

- [API mapping](docs/api-mapping.md)
- [Security model](docs/security.md)
- [Runbook](docs/runbook.md)

