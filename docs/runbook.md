# Runbook

## Start Server

```powershell
$env:UV_CACHE_DIR='C:/Users/j/Desktop/.uv-cache'
cd C:\Users\j\Desktop\fdl-mcp
uv run --python 3.11 --with ".[dev]" -m fdl_mcp.server
```

## Common Incidents

1. `FDL_AUTH_*` failures
- Check `FDL_AUTH_MODE` and required variables.
- Validate key rotation status in FDL backend.

2. `FDL_HTTP_5XX` spikes
- Check FDL backend health and gateway.
- Reduce traffic or increase backoff/retry if safe.

3. `FDL_POLICY_*` blocked requests
- Confirm allow-list and rate limit config.
- Verify caller identity source.

4. Data service 404 in auto mode
- Confirm `FDL_SERVICE_PATH_MODE`.
- If FDL version is known old, set `legacy`.

## Observability Checklist

- Ensure logs include `trace_id`.
- Verify latency percentiles and error-rate alerts.
- Keep idempotency TTL aligned with business replay window.

