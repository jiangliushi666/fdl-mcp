# 安全模型

## 密钥管理

- 所有密钥仅从环境变量加载，不写入代码或配置文件。
- MCP 工具响应中不返回任何密钥信息。
- 审计日志对以下字段自动脱敏：`secret`、`token`、`authorization`、`appcode`、`password`。

## 认证模式

| 模式 | 说明 |
|---|---|
| `aksk` | HMAC-SHA256 签名，设置 `X-FDL-Client-Id`、`X-FDL-Timestamp`、`X-FDL-Signature`、`Authorization: HMAC-SHA256` 头 |
| `appcode` | 兼容模式，设置 `AppCode` 头 |
| `fine_auth_token` | 写链路对齐浏览器：同时发送 `Authorization: Bearer <token>` 与 `Cookie: fine_auth_token=<token>`（可带完整 cookie header） |

## 开发态写链路安全约束

- 适用接口：`/webroot/decision/fdl/dev/work/save`、`/webroot/decision/fdl/dev/work/publish/check`、`/webroot/decision/fdl/dev/work/publish`。
- 写请求必须使用 `fdl-encrypt: encrypted`；读取类请求使用 `fdl-encrypt: plaintext`。
- 当响应头包含 `alreadyencrypted: true` 时，MCP 会自动解密响应。
- 解密后如果是 JSON，直接返回对象；若非 JSON，返回 `{"raw": <plaintext>}`。

## 加密算法边界

- 当前环境已验证链路为：`frontSeed + AES-ECB + PKCS7 + Base64`。
- 当前实现据此在本地执行加密/解密；`FDL_ENCRYPT_KEY` 来源应为页面 `Dec.system.frontSeed`。
- 以上结论只对当前验证环境成立；其它环境可能切换到 SM4 / customEncrypt / 其它实现，需单独抓包与联调验证后再启用。

## 策略守卫（PolicyGuard）

- 工具白名单：`FDL_ALLOWED_TOOLS`（空表示不限制）
- 工作流 ID 白名单：`FDL_ALLOWED_WORK_IDS`
- 工作流名称白名单：`FDL_ALLOWED_WORK_NAMES`
- 限流：`FDL_RATE_LIMIT_PER_MIN`，按调用方 + 工具维度，进程内计数

## 审计日志字段

每次工具调用均记录以下字段：

- `trace_id`：请求唯一标识
- `caller`：调用方身份（来自 `MCP_CALLER` 环境变量，默认取 `USERNAME`）
- `tool_name`：MCP 工具名称
- `fdl_endpoint`：实际请求的 FDL 接口路径
- `status_code`：HTTP 状态码
- `latency_ms`：请求耗时（毫秒）
- `params_summary`：脱敏后的参数摘要
- `error_code`：错误码（成功时为空）
