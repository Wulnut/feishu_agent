<!--
 * @Author: liangyz liangyz@seirobitcs.net
 * @Date: 2026-01-12 12:29:36
 * @LastEditors: liangyz liangyz@seirobitcs.net
 * @LastEditTime: 2026-01-12 12:32:50
 * @FilePath: \feishu_mcp\AGENTS.md
 * @Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
-->

# AGENTS.md: 飞书 Agent 生态开发指南 (Stage 1)

## 1. 项目愿景 (Project Vision)

构建一个从 **飞书项目 (Lark Project)** 起步，逐步演进为具备 **Workflow 编排** 与 **自主推理能力 (Agent)** 的企业级 AI 助手生态。

## 2. 核心技术栈 (Technical Stack)

* **语言**: Python 3.11+ (严格使用类型注解 Type Hints)
* **依赖管理**: `uv` (使用 `pyproject.toml` 和 `uv.lock`)
* **飞书 SDK**: `lark-oapi` (v3.x, 优先使用异步接口 `a` 开头方法)
* **协议层**: MCP (Model Context Protocol) 使用 `FastMCP` 框架
* **环境**: Docker (基于 `python:3.11-slim-bookworm`)
* **异步模型**: 基于 `asyncio` 的 Future/Promise 模式

---

## 3. 架构设计规范 (Architecture Standards)

### 3.1 目录组织

```text
src/
├── core/           # 单例 Client, 配置中心 (pydantic-settings)
├── providers/      # 核心层: 能力者模式实现
│   ├── base.py     # 抽象基类 (Protocol/ABC)
│   ├── common/     # 通用能力 (IM, Base, Drive)
│   └── project/    # 飞书项目专用能力 (Items, Fields, Gantt)
├── schemas/        # 数据模型 (Pydantic), 用于精简 API 返回值
└── mcp_server.py   # MCP 接口层: 注册 Tool 与 Resource

```

### 3.2 OOP 与 Provider 模式

* **封装**: 所有飞书接口调用必须封装在 `Provider` 类中。
* **解耦**: 使用 **Provider 模式**。`mcp_server.py` 只与 `Provider` 抽象接口交互，不直接操作底层 SDK。
* **精简**: Provider 必须对飞书原始 JSON 进行数据清洗，仅向 Agent 返回核心业务字段，以节省 Token。

---

## 4. 开发守则 (Development Rules for Cursor)

### 4.1 异步优先 (Async First)

* 所有的 API 请求必须使用异步方法。
* 示例: 使用 `client.im.v1.message.acreate()` 而不是 `create()`。
* 处理多个并发请求时，使用 `asyncio.gather()`。

### 4.2 错误处理

* 不允许直接抛出飞书 SDK 的原始异常。
* 必须在 Provider 层捕获异常，并返回人类/Agent 可读的中文错误提示。

### 4.3 文档注释 (Docstrings)

* 每个 `mcp.tool()` 必须包含极其详尽的 Docstring。
* **Docstring 必须描述**: 1. 工具的功能；2. 参数的业务含义；3. 预期返回的结果。

---

## 5. 演进路线图 (Roadmap)

1. **Stage 1 (Current)**: 飞书项目 MCP 落地，实现工作项 CRUD 自动化。
2. **Stage 2**: 引入 LangGraph 进逻辑行编排 (Workflow)。
3. **Stage 3**: 完整 Agent 化，支持自然语言决策。

---

## 6. Cursor 指令速查 (Context for Cursor)

> 当我在 Cursor 中要求你开发新功能时，请确保：
> 1. 检查 `src/core/client.py` 确保单例调用。
> 2. 在 `src/providers/` 下按类别创建新的类。
> 3. 在 `main.py` 中使用 `FastMCP` 注册工具。
> 4. 保持代码符合 Python 3.11 的异步高性能标准。