# 测试问题记录

## 测试时间
2026-03-09

## 测试目标
验证 fdl-mcp 能否完成：创建文件夹 claude-1，创建任务 claude-1.1，添加 DB表输入->DB表输出 的数据转换节点，并保存（不运行）

## 测试结果

### ❌ 失败

#### 问题 1: 缺少创建文件夹和任务的功能
- **现象**: fdl-mcp 没有提供创建文件夹和任务实体的 API
- **影响**: 必须手动通过浏览器或其他方式创建任务实体，才能用 fdl-mcp 配置
- **相关接口**:
  - 创建文件夹: `POST /webroot/decision/fdl/dev/catalog/package/create`
  - 创建任务: `POST /webroot/decision/fdl/dev/catalog/entity/create`
- **状态**: 未实现

#### 问题 2: 生成的工作流 payload 有问题
- **现象**:
  - 调用 `build_db_to_db_workflow` 生成 payload
  - 调用 `save_work` 保存，返回 HTTP 200 + Business Code 200 + Result: success
  - 但在 FDL 界面中打开任务时，页面空白，任务无法正常显示
- **测试任务**:
  - Work ID: `8b0cfeb3-e6d2-4e9e-b9d5-ec3092ef0dc4`
  - 路径: claude-1/claude-1.1
- **推测原因**:
  - payload 结构不完整
  - 缺少必需字段
  - 字段值格式不正确
- **状态**: 需要对比真实 payload 找出差异

#### 问题 3: 之前的"权限不足"错误是误判
- **原因**: 使用了错误的 API 方法
  - ❌ 错误: 用 `build_db_to_db_workflow` 直接创建新任务（缺少 parentId 等字段）
  - ✅ 正确: 先创建任务实体，再用 `get_work_development_info` 读取，然后配置并保存
- **教训**: 需要理解 FDL 的任务创建流程

## 已验证的功能

### ✅ 正常工作的部分

1. **连接和认证**
   - 从 .env 加载配置
   - fine_auth_token 认证
   - AES 加密/解密

2. **读取接口**
   - `get_work_development_info` - 读取任务配置
   - `get_global_params` - 读取全局参数
   - `list_connections` - 列出数据库连接
   - `list_functions` - 列出函数

3. **保存接口**
   - `save_work` - 调用成功，返回 200
   - 但保存的数据有问题

## Payload 对比分析结果

### 对比文件
- `working_task_payload.json` - 真实的、能正常工作的任务 payload
- `fdl_mcp_payload.json` - fdl-mcp 生成的 payload

### 结构对比

**顶层结构（两者相同）：**
```json
{
  "workId": "...",
  "checkState": "SUCCESS",
  "workBook": {...},
  "externalJsonStrings": {}
}
```

**workBook 结构（两者相同）：**
```json
{
  "id": "...",
  "name": "...",
  "params": [],
  "notes": [],
  "graph": {...},
  "nodes": [
    {
      "compareId": "...",
      "type": "DATA_FLOW",
      "value": {
        "nodes": [...],
        "lines": [...]
      }
    }
  ],
  "lines": []
}
```

**节点结构对比：**

真实任务（API_INPUT -> PARAM_OUTPUT）：
- nodeType: "API_INPUT", "PARAM_OUTPUT"
- 有 nodeContent 字段
- 有 compareId 字段

fdl-mcp 生成（DB_READ -> DB_WRITE）：
- nodeType: "DB_READ", "DB_WRITE"
- 有 nodeContent 字段
- 有 compareId 字段

### 结论

✅ **fdl-mcp 生成的 payload 结构是正确的！**

问题可能在于：
1. **字段值的细节** - 某些字段的值可能不正确或缺失
2. **节点配置** - DB_READ/DB_WRITE 节点的 nodeContent 配置可能有问题
3. **其他隐藏字段** - 可能缺少某些必需但不明显的字段

### 需要进一步调查

1. 对比 DB_READ/DB_WRITE 节点的 nodeContent 详细配置
2. 检查是否缺少必需的字段（如 samples、createSql 等）
3. 验证字段类型和格式是否正确

## 下一步行动

1. **创建一个手动配置的 DB->DB 任务**
   - 通过浏览器手动创建完整的 DB表输入->DB表输出 任务
   - 读取其 payload，对比 nodeContent 的详细配置

2. **逐字段对比**
   - 对比每个字段的值和格式
   - 找出导致任务无法打开的具体原因

3. **修复并测试**
   - 修正发现的问题
   - 重新测试保存和打开任务

## 相关文件
- 测试脚本: `test_*.py`, `compare_payloads.py`, `read_working_task.py`
- Payload 文件: `working_task_payload.json`, `fdl_mcp_payload.json`
- 配置文件: `.env`
- 源代码: `src/fdl_mcp/dev_services.py`
