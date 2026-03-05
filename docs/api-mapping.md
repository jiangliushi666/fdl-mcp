# API Mapping v1

## MCP Tools -> FDL Endpoint

- `fdl_execute_work_by_id` -> `POST /decision/sp/client/api/fdl/workId/execute`
- `fdl_execute_work_by_name` -> `POST /decision/sp/client/api/fdl/workName/execute`
- `fdl_get_record` -> `GET /decision/sp/client/api/fdl/record/info`
- `fdl_list_records` -> `GET /decision/sp/client/api/fdl/record/list` (fallback `/decision/sp/client/api/fdl/records/list`)
- `fdl_terminate_records` -> `POST /decision/sp/client/api/fdl/records/terminate`
- `fdl_terminate_work` -> list records by workflow target + terminate record IDs
- `fdl_call_data_service` -> `/service/{AppId}/{ApiPath}` then fallback `/service/publish/{AppId}/{ApiPath}` in `auto` mode
- `fdl_healthcheck` -> local config and policy health, plus optional lightweight remote request

## Error Prefixes

- `FDL_AUTH_*`
- `FDL_HTTP_*`
- `FDL_TASK_*`
- `FDL_POLICY_*`

