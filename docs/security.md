# Security Model

## Secret Handling

- Secrets are loaded from environment only.
- Secrets are never returned by MCP tools.
- Audit logs redact sensitive fields: `secret`, `token`, `authorization`, `appcode`.

## Authentication

Supported modes:

- `aksk`: HMAC-SHA256 signature headers
- `appcode`: `AppCode` header compatibility mode
- `fine_auth_token`: `Authorization: Bearer <token>`

## Policy Guard

- Tool allow-list via `FDL_ALLOWED_TOOLS`
- Workflow allow-list via `FDL_ALLOWED_WORK_IDS`, `FDL_ALLOWED_WORK_NAMES`
- Rate limit per caller/tool via `FDL_RATE_LIMIT_PER_MIN`

## Audit Fields

- `trace_id`
- `caller`
- `tool_name`
- `fdl_endpoint`
- `status_code`
- `latency_ms`
- redacted params summary

