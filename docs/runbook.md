# 运维手册

## 启动服务

```powershell
$env:UV_CACHE_DIR='C:/Users/j/Desktop/.uv-cache'
cd C:\Users\j\Desktop\fdl-mcp
uv run --python 3.11 --with ".[dev]" -m fdl_mcp.server
```

## 测试阶段 save-only 流程（严禁 publish / 定时）

适用场景：真实环境联调时，仅验证开发态写链路 save 闭环。

1. 配置工具白名单护栏（强制只放行 save 所需工具）。

```powershell
$env:FDL_ALLOWED_TOOLS='fdl_dev_configure_chrome_session,fdl_dev_build_db_to_db_workflow,fdl_dev_save_work,fdl_dev_save_db_to_db_workflow'
```

说明：
- `fdl_dev_save_work` 与 `fdl_dev_save_db_to_db_workflow` 二选一即可；可按实际精简白名单。
- 必须显式排除：`fdl_dev_publish_work_check`、`fdl_dev_publish_work`、所有调度相关工具。

2. 从已登录页面提取会话并调用 `fdl_dev_configure_chrome_session(page_data)`。
   - 必须包含：`origin`、`cookie(含 fine_auth_token)`、`frontSeed`。

3. 在目标（如 `DEMO示例`）构造或复用 save payload。

4. 仅调用一次 save 工具：
   - `fdl_dev_save_work(payload)` 或
   - `fdl_dev_save_db_to_db_workflow(...)`

5. 验证结果并记录：
   - HTTP `200`
   - endpoint 为 `/webroot/decision/fdl/dev/work/save`
   - 返回体可解析（或符合 `{"raw": ...}` 预期）
   - 记录 `trace_id`、work 标识、时间戳至 `docs/handoff.md`

### 硬停止条件

出现以下任一情况必须立即停止并回滚到 save-only 范围：
- 触发 `fdl_dev_publish_work_check`
- 触发 `fdl_dev_publish_work`
- 触发任何 schedule / execute / publish 相关操作

## 常见故障处理

### 1. `FDL_AUTH_*` 认证失败

- 检查 `FDL_AUTH_MODE` 与对应必填变量是否配置正确。
- 确认 FDL 后端密钥是否已轮换，及时更新 `FDL_SECRET` 或 `FDL_APPCODE`。

### 2. `FDL_HTTP_5XX` 错误率上升

- 检查 FDL 后端服务和网关健康状态。
- 如情况允许，适当降低请求频率或增大 `FDL_RETRY_MAX` 的退避间隔。

### 3. `FDL_POLICY_*` 请求被拦截

- 确认白名单配置（`FDL_ALLOWED_TOOLS`、`FDL_ALLOWED_WORK_IDS`、`FDL_ALLOWED_WORK_NAMES`）。
- 检查限流配置 `FDL_RATE_LIMIT_PER_MIN` 是否合理。
- 确认调用方身份来源（`MCP_CALLER` 环境变量）。

### 4. 数据服务 auto 模式下 404

- 确认 `FDL_SERVICE_PATH_MODE` 配置。
- 如已知 FDL 版本较旧，将 `FDL_SERVICE_PATH_MODE` 设为 `legacy`。

### 5. 幂等键重启后失效

- 当前幂等存储为内存级别，进程重启后所有幂等键丢失。
- 如需持久化重放保护，需替换为 Redis 或数据库存储（v2 规划项）。

## 可观测性检查清单

- 确认日志中包含 `trace_id`，便于端到端追踪。
- 监控错误率和延迟百分位（p99）。
- 确保 `FDL_IDEMPOTENCY_TTL_SEC` 与业务重放窗口对齐。
- 多实例部署时注意限流不共享，需引入共享计数器。
