# FDL-MCP 项目交接文档

## 项目概述

**项目名称**: fdl-mcp
**项目路径**: `C:\Users\j\Desktop\fdl-mcp`
**项目目标**: 为 FineDataLink (FDL) 提供 MCP (Model Context Protocol) 接口，实现任务自动化管理

## 测试环境

### FDL 实例信息
- **地址**: http://192.168.138.35:8068
- **账号**: fdlxm
- **密码**: 2383566697x
- **登录页面**: http://192.168.138.35:8068/webroot/decision/login

### 环境配置文件
- **配置文件**: `.env` (已创建)
- **认证模式**: fine_auth_token (从浏览器自动提取)
- **加密模式**: aes
- **加密密钥**: 1ED6F5BA8CFD75F8 (frontSeed)

## 当前状态

### ✅ 已验证的功能

1. **连接和认证**
   - 从 .env 加载配置 ✓
   - fine_auth_token 认证 ✓
   - AES 加密/解密 ✓

2. **读取接口**
   - `get_work_development_info` - 读取任务配置 ✓
   - `get_global_params` - 读取全局参数 ✓
   - `list_connections` - 列出数据库连接 ✓
   - `list_functions` - 列出函数 ✓

3. **保存接口**
   - `save_work` - 调用成功，返回 HTTP 200 ✓
   - **但保存的数据有问题，任务无法打开** ✗

### ❌ 存在的问题

#### 问题 1: 缺少创建功能
- **现象**: fdl-mcp 没有提供创建文件夹和任务实体的 API
- **影响**: 必须手动创建任务实体，才能用 fdl-mcp 配置
- **相关接口**:
  - 创建文件夹: `POST /webroot/decision/fdl/dev/catalog/package/create`
  - 创建任务: `POST /webroot/decision/fdl/dev/catalog/entity/create`

#### 问题 2: 生成的任务无法打开（核心问题）
- **现象**:
  - 调用 `build_db_to_db_workflow` 生成 payload
  - 调用 `save_work` 保存，返回 HTTP 200 + Business Code 200
  - 但在 FDL 界面中打开任务时，页面空白
- **测试任务**:
  - Work ID: `8b0cfeb3-e6d2-4e9e-b9d5-ec3092ef0dc4`
  - 路径: claude-1/claude-1.1
- **已排查**:
  - ✓ Payload 顶层结构正确（有 workBook、nodes、lines）
  - ✓ DATA_FLOW 节点类型正确
  - ✗ 具体的 nodeContent 配置可能有问题

## 已完成的调查工作

### Payload 结构对比

**对比文件**:
- `working_task_payload.json` - 真实的、能正常工作的任务 (API_INPUT->PARAM_OUTPUT)
- `fdl_mcp_payload.json` - fdl-mcp 生成的任务 (DB_READ->DB_WRITE)

**对比结果**:
- 顶层结构相同 ✓
- workBook 结构相同 ✓
- 节点结构相同 ✓
- **但缺少 DB_READ->DB_WRITE 的真实任务对比** ✗

### 测试脚本

已创建的测试脚本（在项目根目录）:
- `test_connection.py` - 基本连接测试
- `test_full.py` - 完整功能测试
- `test_create_workflow.py` - 工作流创建测试
- `compare_payloads.py` - Payload 对比脚本
- `read_working_task.py` - 读取任务脚本
- `complete_claude_task.py` - 完成测试任务脚本

## 下一步行动计划

### 第一步：创建对比基准

1. **手动创建 DB->DB 数据同步任务**
   ```
   任务名称: db-sync-reference
   源表: finedb (MySQL) -> columns_priv 表
   目标表: finedb (MySQL) -> jjvu_data_ods.columns_priv
   建表模式: 自动建表
   同步模式: OVERWRITE
   ```

2. **保存任务并获取 work_id**
   - 在浏览器中完成配置
   - 保存任务
   - 从网络请求中获取 work_id

3. **读取真实 payload**
   ```bash
   cd C:/Users/j/Desktop/fdl-mcp
   export UV_CACHE_DIR='C:/Users/j/Desktop/.uv-cache'

   # 修改 read_working_task.py 中的 work_id
   # 然后运行
   uv run --python 3.11 --with ".[dev]" --with python-dotenv python read_working_task.py
   ```

### 第二步：详细对比

1. **对比 DB_READ 节点的 nodeContent**
   - 重点字段: `fromDatasourceType`, `fromConnectionName`, `dataBaseConfig`, `samples`
   - 检查是否缺少字段或值不正确

2. **对比 DB_WRITE 节点的 nodeContent**
   - 重点字段: `type`, `toDatasourceType`, `toConnectionName`, `toDatabase`, `toSchema`, `toTable`, `toTableMode`, `writeType`, `writeConfig`, `fieldTransferItems`
   - 检查字段格式和值

3. **记录差异**
   - 创建详细的差异对比文档
   - 标注哪些字段缺失或不正确

### 第三步：修复代码

1. **修改 `src/fdl_mcp/dev_services.py`**
   - 定位到 `build_db_read_node_template` 方法
   - 定位到 `build_db_write_node_template` 方法
   - 根据差异修正字段

2. **重新测试**
   ```bash
   # 生成新的 payload
   uv run --python 3.11 --with ".[dev]" --with python-dotenv python compare_payloads.py

   # 测试保存
   uv run --python 3.11 --with ".[dev]" --with python-dotenv python complete_claude_task.py
   ```

3. **验证任务可以打开**
   - 在 FDL 界面中打开任务
   - 确认节点配置正确显示
   - 确认可以正常编辑

### 第四步：补充缺失功能

1. **实现创建文件夹 API**
   ```python
   async def create_package(self, parent_id: str, package_name: str, describe: str = "") -> tuple[Any, int, str]:
       return await self.client.request_fdl_dev(
           "POST",
           "/webroot/decision/fdl/dev/catalog/package/create",
           body={
               "parentId": parent_id,
               "parentPath": [],
               "nodeName": package_name,
               "describe": describe
           }
       )
   ```

2. **实现创建任务实体 API**
   ```python
   async def create_entity(self, parent_id: str, parent_path: list, entity_name: str, describe: str = "") -> tuple[Any, int, str]:
       return await self.client.request_fdl_dev(
           "POST",
           "/webroot/decision/fdl/dev/catalog/entity/create",
           body={
               "parentId": parent_id,
               "parentPath": parent_path,
               "nodeName": entity_name,
               "describe": describe
           }
       )
   ```

3. **添加到 server.py 并测试**

## 重要文件清单

### 文档
- `docs/test-issues.md` - 详细问题记录
- `docs/test-environment.md` - 测试环境配置（含账号密码）
- `docs/investigation-summary.md` - 调查结果总结
- `docs/handoff.md` - 原有的交接文档
- `docs/dev-node-capability-matrix.md` - 节点能力矩阵
- `docs/dev-capability-boundary.md` - 能力边界说明

### 配置
- `.env` - 环境配置（含 token 和加密密钥）
- `pyproject.toml` - 项目配置

### 源代码
- `src/fdl_mcp/dev_services.py` - 核心服务类（需要修复）
- `src/fdl_mcp/server.py` - MCP 服务器
- `src/fdl_mcp/client.py` - HTTP 客户端
- `src/fdl_mcp/config.py` - 配置管理

### 测试数据
- `working_task_payload.json` - 真实任务 payload (API_INPUT->PARAM_OUTPUT)
- `fdl_mcp_payload.json` - fdl-mcp 生成的 payload (DB_READ->DB_WRITE)

## 快速启动命令

### 设置环境
```bash
cd C:/Users/j/Desktop/fdl-mcp
export UV_CACHE_DIR='C:/Users/j/Desktop/.uv-cache'
```

### 运行测试
```bash
# 基本连接测试
uv run --python 3.11 --with ".[dev]" --with python-dotenv python test_full.py

# Payload 对比
uv run --python 3.11 --with ".[dev]" --with python-dotenv python compare_payloads.py

# 读取任务
uv run --python 3.11 --with ".[dev]" --with python-dotenv python read_working_task.py
```

### 启动 MCP 服务器
```bash
uv run --python 3.11 --with ".[dev]" -m fdl_mcp.server
```

## 关键发现和教训

1. **Payload 结构是正确的** - 不要被表面现象误导，需要深入到字段级别对比
2. **需要真实的对比基准** - 必须有相同类型的任务才能准确对比
3. **Save 成功不代表数据正确** - FDL 的 save 接口可能不会严格校验所有字段
4. **文档很重要** - 每次调查都要及时记录，避免重复工作

## 联系方式

- **项目位置**: C:\Users\j\Desktop\fdl-mcp
- **FDL 地址**: http://192.168.138.35:8068
- **测试账号**: fdlxm / 2383566697x

## 最后更新

- **日期**: 2026-03-09
- **状态**: 调查中，已确定问题方向，等待详细对比
- **下一步**: 创建 DB->DB 对比基准任务
