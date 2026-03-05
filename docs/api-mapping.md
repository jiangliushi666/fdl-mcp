# API 映射表 v1

## MCP 工具 → FDL 接口

| MCP 工具 | FDL 接口 |
|---|---|
| `fdl_execute_work_by_id` | `POST /decision/sp/client/api/fdl/workId/execute` |
| `fdl_execute_work_by_name` | `POST /decision/sp/client/api/fdl/workName/execute` |
| `fdl_get_record` | `GET /decision/sp/client/api/fdl/record/info` |
| `fdl_list_records` | `GET /decision/sp/client/api/fdl/record/list`（fallback: `/decision/sp/client/api/fdl/records/list`） |
| `fdl_terminate_records` | `POST /decision/sp/client/api/fdl/records/terminate` |
| `fdl_terminate_work` | 先查询工作流下的运行记录，再批量终止 |
| `fdl_call_data_service` | `/service/{AppId}/{ApiPath}`，auto 模式下 404 时回退到 `/service/publish/{AppId}/{ApiPath}` |
| `fdl_healthcheck` | 返回本地配置和策略状态（不发起远程请求） |

## 错误码前缀

| 前缀 | 含义 |
|---|---|
| `FDL_AUTH_*` | 认证/鉴权失败 |
| `FDL_HTTP_*` | HTTP 层错误 |
| `FDL_TASK_*` | 任务服务层错误 |
| `FDL_POLICY_*` | 策略拦截（白名单、限流） |
