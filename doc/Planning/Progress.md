# 项目进度跟踪 (Progress Tracking)

## Stage 1: 飞书项目 MCP 落地 (Current)

目标：实现工作项（Issue）的增删改查自动化，支持动态元数据发现，消除硬编码。

### ✅ 已完成 (Completed)

#### 1. 架构重构 (Infrastructure)
- [x] **架构分层**: 确立了 Interface (MCP) -> Service (Provider) -> Data (API) -> Infrastructure (Core) 的四层架构。
- [x] **核心模块**:
    - `src/core/project_client.py`: 增强 HTTP 客户端，支持 PUT/DELETE。
    - `src/providers/project/api/work_item.py`: 封装纯粹的 REST API 调用。
    - `src/providers/project/services/metadata.py`: 实现元数据动态发现与缓存服务。
    - `src/providers/project/work_item_provider.py`: 业务逻辑编排，串联 API 与 Metadata。

#### 2. 核心功能 (Features)
- [x] **Issue CRUD**:
    - 创建 (`create_issue`): 支持动态字段解析（如优先级 "P2" -> "option_3"）。
    - 查询 (`get_issue_details`): 支持字段展开。
    - 删除 (`delete_issue`).
    - 更新 (`update_issue`): 已验证描述更新，优先级更新受限于 API 限制但已做异常处理。
- [x] **动态发现**:
    - 项目 Key 动态查找。
    - 字段 Key (如 "description") 动态查找。
    - 选项 Value (如 "P2") 动态解析。
- [x] **复杂过滤**:
    - 实现了关联字段（如 "关联项目"）的客户端过滤方案。

#### 3. 文档与规范 (Documentation)
- [x] **技术方案**: 更新 `doc/Feishu_agent_plan.md`，明确分层架构。
- [x] **操作指南**:
    - `doc/Feishu_project_api/格式说明/工作项CRUD操作指南.md`
    - `doc/Feishu_project_api/格式说明/工作项过滤方法汇总.md`
    - `doc/Feishu_project_api/格式说明/脚本硬编码问题分析.md`

#### 4. 测试验证 (Testing)
- [x] **单元测试**: `tests/providers/project/` 下覆盖了 Provider, Service, API 层。
- [x] **集成脚本**: `scripts/work_items/test_provider_stack.py` 验证了全链路逻辑。

---

### 🚧 进行中 / 下一步 (In Progress / Next Steps)

#### 1. MCP 接口完善
- [ ] **Tools 定义**: 完善 `mcp_server.py` 中的 `create_task` 等工具，使其参数定义更准确（利用 Pydantic）。
- [ ] **Filter Tool**: 暴露 `filter_issues` 能力给 LLM。

#### 2. 关联字段支持
- [ ] **API 封装**: 将 `filter_issues_by_project.py` 中的关联字段过滤逻辑封装进 `WorkItemProvider`。

#### 3. 错误处理与健壮性
- [ ] **Retry 机制**: 在 `ProjectClient` 中增加请求重试。
- [ ] **更友好的错误提示**: 当字段解析失败时，提供可用的选项列表。

---

## Stage 2: Workflow 编排 (Planned)

目标：引入 LangGraph，支持多步骤任务执行。

- [ ] 设计 Workflow State Schema。
- [ ] 实现 "需求 -> 任务拆解 -> 批量创建" 的 Workflow。

## Stage 3: Agent 自主进化 (Planned)

目标：具备语义理解与决策能力。

- [ ] 接入向量数据库，支持知识库问答。
- [ ] 实现基于 ReAct 的自主规划。
