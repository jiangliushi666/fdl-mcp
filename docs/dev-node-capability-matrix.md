# 数据开发节点能力矩阵（造轮子阶段）

> 目标：把“已确认能力”与“待落地能力”统一成单一真相，按证据级别与实现状态推进。

## 状态定义

- `done`：已实现 + 测试通过 + 至少一次真实 save-only 验证（若适用）
- `in_progress`：已进入开发，但未完成 DoD
- `planned`：已纳入计划，未开发

## 证据级别

- `L3`：真实联调验证
- `L2`：抓包/页面行为验证
- `L1`：代码/静态推断

## 能力矩阵（当前）

### A. 已建模节点子集（当前代码与测试已覆盖）

| 能力域 | 节点/能力 | 证据 | 实现状态 | 备注 |
|---|---|---:|---|---|
| 输入 | DB表输入（DB_READ） | L3 | done | 已有节点级 builder、模板级 builder、测试与 save-only 实测链路 |
| 输入 | API输入（API_INPUT） | L3 | done | 已有节点级 builder、模板级 builder、测试与 API_INPUT→PARAM_OUTPUT save-only 证据 |
| 输入 | 文件输入（FILE_INPUT） | L3 | done | 已有节点级 builder、模板级 builder、测试与 FILE_INPUT->DB_WRITE save-only 证据 |
| 输出 | DB表输出（DB_WRITE） | L3 | done | 已有节点级 builder、模板级 builder、测试与 save-only 实测链路 |
| 输出 | 参数输出（PARAM_OUTPUT） | L3 | done | 已有节点级 builder、模板级 builder、测试与 API_INPUT→PARAM_OUTPUT save-only 证据 |
| 输出 | 文件输出（FILE_OUTPUT） | L3 | done | 已有节点级 builder、模板级 builder、测试与 DB_READ->FILE_OUTPUT save-only 证据 |
| 处理 | 数据关联（JOIN） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | 数据比对（DATA_COMPARE） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | 上下合并（UNION） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | 列转行（UNPIVOT） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | JSON解析（JSON_PARSE） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | 行过滤（ROW_FILTER） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | 字段选择/映射（FIELD_SELECT） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | 排序（SORT） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 处理 | 聚合（AGGREGATE） | L3 | done | 已完成模板 builder、测试与 save-only 实测闭环 |
| 脚本 | SQL脚本（SQL_SCRIPT） | L1 | done | 已有节点级 builder、组合模板 builder 与测试；当前文档未记录独立 L3 节点实证 |
| 脚本 | Python脚本（PYTHON_SCRIPT） | L1 | done | 已有节点级 builder、组合模板 builder 与测试；当前文档未记录独立 L3 节点实证 |
| 流程类 | 条件分支（CONDITION_BRANCH） | L1 | done | 已有节点级 builder、组合模板 builder 与测试；当前文档未记录 L3 实证 |
| 流程类 | 参数赋值（PARAM_ASSIGN） | L1 | done | 已有节点级 builder、组合模板 builder 与测试；当前文档未记录 L3 实证 |
| 流程类 | 汇聚（MERGE） | L1 | done | 已有节点级 builder、组合模板 builder 与测试；当前文档未记录 L3 实证 |
| 流程类 | 调用任务（CALL_TASK） | L1 | done | 已有节点级 builder、组合模板 builder 与测试；当前文档未记录 L3 实证 |
| 流程类 | 文件传输（FILE_TRANSFER） | L3 | done | 已有节点级 builder、模板级 builder、测试与 FILE_TRANSFER save-only 证据 |
| 流程类 | 数据同步模式参数化 | L3 | done | DB→DB / FILE→DB 模板参数已扩展并完成 save-only 实测 |
| 批量化 | 批量模板渲染（表清单→payload） | L1 | in_progress | 本地批量 render helper + MCP tool + 测试已落地，待真实 save-only 配套使用确认 |
| 批量化 | 批量 save-only 执行与汇总 | L1 | in_progress | 顺序 `/work/save` 编排 + 汇总结果结构 + 测试已落地，待真实联调 |

### B. 页面/API 已确认、但仓库尚未完全建模的能力

| 类型 | 项目 | 证据 | 当前状态 | 说明 |
|---|---|---:|---|---|
| 节点覆盖 | Spark SQL 页面节点 | L2 | planned | 已确认页面存在与节点配置入口，但尚未确认保存 payload 语义，暂不建模 builder |
| 节点覆盖 | Python 页面节点与 `PYTHON_SCRIPT` 的同义性 | L2 | in_progress | 已确认页面存在、代码编辑区与输入输出配置，但仍需 payload 级对照确认是否与当前 builder 完全一致 |
| 节点覆盖 | SQL 页面节点与 `SQL_SCRIPT` 的同义性 | L2 | in_progress | 已确认页面存在，但仍需 payload 级对照确认是否与当前 builder 完全一致 |
| 拓扑 | 节点连接/端口/边 | L2 | planned | 已确认设计器存在 ports/edges/topology 连接语义；后续读取/回填类工具需显式建模连接关系 |
| 读取类 | 工作流目录实体创建 | L2 | planned | 已确认 `POST /webroot/decision/fdl/dev/catalog/entity/create` |
| 读取类 | 工作流目录实体信息 | L2 | done | 已有 `fdl_dev_get_catalog_entity_info`，当前为读取类工具，无需 save-only 证据 |
| 读取类 | 开发中任务定义读取 | L2 | done | 已有 `fdl_dev_get_work_development_info`，读取设计器核心定义 |
| 开发辅助 | 表达式函数列表 | L2 | done | 已有 `fdl_dev_list_functions`，可用于表达式补全/校验 |
| 开发辅助 | 资源锁 | L2 | planned | 已确认 `POST /webroot/decision/fdl/resource/try2lock`，后续涉及编辑态协同需纳入考虑 |
| 开发辅助 | 下游依赖/影响范围读取 | L2 | done | 已有 `fdl_dev_get_downstream`，用于任务关系/影响范围读取 |

### C. 已知缺口与待梳理项

| 类型 | 项目 | 当前状态 | 说明 |
|---|---|---|---|
| 节点覆盖 | Spark SQL 等页面已有但仓库未建模的节点 | planned | 已有 L2 页面证据；下一步需确认页面语义、载荷结构，再决定 builder 设计 |
| 节点覆盖 | Python 节点与当前 `PYTHON_SCRIPT` 是否完全同义 | in_progress | 已有 L2 页面证据；仍需对照真实 payload 确认是否存在额外配置项 |
| 节点覆盖 | SQL 节点与当前 `SQL_SCRIPT` 是否完全同义 | in_progress | 已有 L2 页面证据；仍需对照真实 payload 确认是否存在额外配置项 |
| 读取类 | 工作流目录/树/检索 | planned | 已确认部分目录相关 endpoint，仓库暂未系统化实现 |
| 读取类 | 开发中任务详情读取 | planned | 已确认 development 读取 endpoint，仓库暂未实现对应 MCP 工具 |
| 读取类 | 节点详情读取/回填 | planned | 已确认设计器存在节点配置与连接拓扑，但仓库暂未实现 |
| 检查类 | 保存后更多校验/检查 | planned | 当前仅有 `save/publish-check/publish` 底座与部分辅助 payload 工具 |
| 发布类 | 更多发布前置检查与结果读取 | planned | 尚未系统化建模 |
| 开发辅助 | 参数、变量、依赖任务、版本差异等能力 | planned | 已确认全局参数、函数列表、下游关系等部分基础接口，尚待逐项盘点与映射 |

## 分阶段落地计划（持久化）

### Phase 0（当前）
- 固化能力台账与证据分级（本文件 + 边界文档）。
- DoD 与推进节奏对齐到 handoff。

### Phase 1（高频输入/输出补齐）
- 落地 `API输入`、`参数输出` 的 node builder 与模板装配。
- 补测试：builder 测试、server 工具测试、save-only 断言。
- 在真实环境完成一次 save-only 验证（不触发 publish/check/schedule）。

### Phase 2（核心转换节点）
- 落地：数据关联、数据比对、上下合并、列转行、JSON解析。
- 每个节点按 DoD 完成：文档映射、工具实现、测试通过、save-only 验证记录。

### Phase 3（同步/文件传输）
- 落地文件传输相关节点、同步模式关键参数结构。
- 提供最小可复用模板并通过 save-only 验证。

### Phase 4（批量造轮子能力）
- 落地批量模板渲染器（表清单驱动）。
- 落地批量 save-only 执行器（结果汇总、失败项可重试）。

## DoD（完成定义）

一个能力项标记 `done` 必须满足：
1. `docs/api-mapping.md` 或相关文档有明确映射与约束。
2. MCP 工具可调用且参数稳定。
3. 对应测试通过（单测/集成）。
4. 真实环境至少一次 save-only 验证通过（若适用）。
5. `docs/handoff.md` 有可追溯记录（含 trace_id/时间/目标）。
