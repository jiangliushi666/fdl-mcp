# 测试环境配置指南

## 本地测试环境信息

### 环境地址
- **FDL 地址**: http://192.168.138.35:8068
- **登录页面**: http://192.168.138.35:8068/webroot/decision/login
- **数据开发**: http://192.168.138.35:8068/webroot/decision#preparation

### 测试账号
- **用户名**: fdlxm
- **密码**: 2383566697x

### 自动提取的配置信息
- **fine_auth_token**: 已从浏览器 cookie 自动提取
- **frontSeed (加密密钥)**: `1ED6F5BA8CFD75F8`
- **认证模式**: fine_auth_token
- **加密模式**: aes

## 快速开始

### 方式 1: 使用已配置的 .env 文件

项目根目录已创建 `.env` 文件，包含完整配置。直接运行测试：

```bash
cd C:/Users/j/Desktop/fdl-mcp

# 设置 UV 缓存目录
export UV_CACHE_DIR='C:/Users/j/Desktop/.uv-cache'

# 运行连接测试
uv run --python 3.11 --with ".[dev]" python test_connection.py
```

### 方式 2: 手动设置环境变量

如果不想使用 .env 文件，可以手动设置：

```bash
export FDL_BASE_URL='http://192.168.138.35:8068'
export FDL_AUTH_MODE='fine_auth_token'
export FDL_FINE_AUTH_TOKEN='<从浏览器提取的 token>'
export FDL_ENCRYPT_MODE='aes'
export FDL_ENCRYPT_KEY='1ED6F5BA8CFD75F8'
```

### 方式 3: 使用 Chrome 会话自动提取（推荐）

通过 MCP 工具从已登录的浏览器自动提取配置：

```python
# 在 MCP 客户端中调用
fdl_dev_configure_chrome_session({
    "origin": "http://192.168.138.35:8068",
    "href": "http://192.168.138.35:8068/webroot/decision#preparation",
    "cookie": "<浏览器 cookie>",
    "frontSeed": "1ED6F5BA8CFD75F8"
})
```

## 测试步骤

### 1. 基本连接测试

测试脚本会验证：
- ✓ 配置加载
- ✓ 客户端创建
- ✓ 读取全局参数（低风险）
- ✓ 列出数据库连接（低风险）

### 2. Save-Only 测试

**重要约束**：
- ✓ 只调用 `/webroot/decision/fdl/dev/work/save` 接口
- ✗ 不调用 publish/check 接口
- ✗ 不调用 schedule 接口
- ✗ 不实际运行任务

测试流程：
1. 提供一个已存在的 work_id
2. 读取该任务的开发信息
3. 调用 save 接口（保持原配置不变）
4. 验证返回结果（HTTP 200 + business code 200）

### 3. 可用的测试任务

从运维中心看到的任务列表：
- `DEMO示例/claude` (work_id 需要从界面获取)
- `DEMO示例/抓包测试`
- `ods/test`

## 安全策略

当前 `.env` 配置了工具白名单：
```
FDL_ALLOWED_TOOLS=fdl_dev_configure_chrome_session,fdl_dev_save_work,fdl_dev_get_global_params,fdl_dev_list_connections,fdl_dev_get_development_instance_info,fdl_dev_list_functions,fdl_dev_get_downstream,fdl_dev_get_catalog_entity_info
```

这意味着：
- ✓ 允许读取类操作
- ✓ 允许 save-only 操作
- ✗ 禁止 publish 操作
- ✗ 禁止 schedule 操作

## 注意事项

1. **Token 过期**: fine_auth_token 会过期，过期后需要重新登录并提取
2. **加密密钥**: frontSeed 可能在系统重启后变化，需要重新提取
3. **测试范围**: 当前仅测试 save-only，不涉及发布和运行
4. **环境隔离**: 本配置仅用于本地测试环境，不要用于生产环境

## 故障排查

### 问题 1: 认证失败 (401/403)
- 检查 fine_auth_token 是否过期
- 重新登录浏览器并提取 token

### 问题 2: 加密/解密失败
- 检查 FDL_ENCRYPT_KEY 是否正确
- 从浏览器控制台执行 `Dec.system.frontSeed` 获取最新值

### 问题 3: 连接超时
- 检查网络连接
- 确认 FDL 服务是否正常运行
- 尝试增加 FDL_TIMEOUT_MS

### 问题 4: Save 接口返回错误
- 检查 work_id 是否存在
- 检查 payload 结构是否正确
- 查看返回的 trace_id 和错误信息

## 下一步

测试通过后，可以：
1. 补充更多节点类型的测试
2. 验证批量操作功能
3. 测试复杂工作流的构建
4. 完善错误处理和重试逻辑
