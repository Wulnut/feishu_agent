# 测试实施计划 (Test Implementation Plan)

**版本**: v1.0
**日期**: 2026-01-14
**状态**: 已完成 ✓

根据 `doc/Test_planning/Test_Planning_1.md` 的分析与后续讨论，制定本实施计划。

## 1. 核心决策 (Core Decisions)

*   **执行顺序**: P0（Schema 增强 + 断言重构） -> P1（Provider 深度测试） -> P2（双轨制测试基础设施）。
*   **目录结构**: 采用 **分离目录结构** (`tests/unit` vs `tests/integration`)，明确隔离单元测试与集成测试。
*   **双轨制测试 (Dual-Track)**:
    *   **Track 1 (Unit)**: 使用从 Track 2 自动抓取的真实 API 快照 (`tests/fixtures/snapshots`)。
    *   **Track 2 (Integration)**: 在真实飞书环境（主流程测试空间）运行 E2E 测试。
*   **测试环境**:
    *   项目: 主流程测试空间 (`project_key=66bb463229e5e58856b4ed19`)
    *   工作项类型: `Issue管理`
    *   CI/CD: 集成到 GitHub Actions，通过 `pytest.mark.integration` 控制运行。

## 2. 目录结构变更 (Directory Restructuring)

```text
tests/
├── conftest.py                     # 全局配置 (Fixture, Markers)
├── fixtures/
│   └── snapshots/                  # [新增] 真实 API 响应快照 (JSON)
│       └── .gitkeep
├── unit/                           # [迁移] 所有现有单元测试
│   ├── core/
│   ├── providers/
│   ├── schemas/
│   ├── services/
│   ├── test_main.py
│   └── test_mcp_server.py
└── integration/                    # [新增] 集成测试
    ├── conftest.py                 # 集成测试专用 Fixtures
    └── test_work_item_e2e.py       # E2E 流程测试
```

## 3. 详细任务列表 (Task List)

### Phase 0: 基础设施重构 (Infrastructure)
- [x] **Task 0.1**: 创建新的目录结构 (`unit`, `integration`, `fixtures/snapshots`)。
- [x] **Task 0.2**: 迁移现有测试文件到 `tests/unit/` 下，并修复 import 路径。
- [x] **Task 0.3**: 更新 `tests/conftest.py`，注册 `integration` marker。

### Phase 1: 单元测试增强 (Unit Tests Enhancement)
- [x] **Task 1.1 (Schema)**: 更新 `tests/unit/schemas/test_models.py`。
    - 增加 `WorkItem` 边界测试（缺少必填字段、类型错误）。
    - 增加 `Pagination` 容错测试（total 为字符串/None）。
- [x] **Task 1.2 (MCP Server)**: 重构 `tests/unit/test_mcp_server.py`。
    - 移除 `assert "成功" in result` 风格断言。
    - 改为 `json.loads(result)` 后验证结构化数据。

### Phase 2: Provider 深度测试 (Provider Logic)
- [x] **Task 2.1**: 更新 `tests/unit/providers/project/test_work_item_provider.py`。
    - 增加异常流测试（项目不存在、API 错误）。
    - 增加分页边界测试。

### Phase 3: 双轨制测试实现 (Dual-Track Implementation)
- [x] **Task 3.1 (Track 1)**: 实现快照加载器。
    - 在 `tests/conftest.py` 中添加 `load_snapshot(name)` fixture。
- [x] **Task 3.2 (Track 2)**: 编写集成测试 `tests/integration/test_work_item_e2e.py`。
    - 配置测试空间与鉴权。
    - 实现完整 CRUD 流程：Create -> Get -> Update -> Delete。
    - **关键点**: 在测试过程中将 API 响应自动保存为 JSON 文件到 `tests/fixtures/snapshots/`。
- [x] **Task 3.3 (CI)**: 配置 CI Workflow 支持集成测试（手动触发）。

## 4. 执行记录 (Execution Log)

*   [已完成] Phase 0: 基础设施重构 ✓
*   [已完成] Phase 1: 单元测试增强 ✓
*   [已完成] Phase 2: Provider 深度测试 ✓
*   [已完成] Phase 3: 双轨制测试实现 ✓

## 5. 测试统计 (Test Statistics)

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 单元测试总数 | 135 | 159 |
| Schema 测试 | 3 | 19 |
| Provider 测试 | 10 | 18 |
| 集成测试 | 0 | 3 |
