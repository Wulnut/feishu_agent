# Feishu Agent 技术方案

## 1. 技术栈选型 (Technical Stack)

| 维度 | 选择 | 理由 |
| --- | --- | --- |
| **编程语言** | **Python 3.11** | 性能优异，原生支持现代异步语法，Agent 生态最成熟。 |
| **开发 SDK** | **`lark-oapi` (v3.x)** | 飞书官方维护，支持全量 API 且完美适配异步调用。 |
| **包管理** | **`uv`** | 2026 年主流，极速安装依赖并自带虚拟环境管理。 |
| **运行环境** | **Docker** | 实现环境隔离与无状态部署，方便未来在云端水平扩展。 |
| **核心协议** | **MCP (Model Context Protocol)** | 跨模型标准协议，确保工具能被任何主流 LLM 调用。 |

## 2. 核心架构设计 (Architecture & Design)

我们将采用**分层模块化**的目录结构，并深度结合 **OOP（面向对象）** 与 **Provider（能力者）模式**。

* **分层设计**：
* **Core 层**：单例模式封装 `LarkClient`，管理 Token 和连接池。
* **Tools - Common 层**：原子化的飞书基础能力（IM、Base、Drive）。
* **Tools - Project 层**：按 API 类别封装的业务逻辑（工作项查询、排期同步）。

* **Provider 模式**：
* 定义通用的能力接口（如 `TaskProvider`），将“飞书项目”的具体实现与“Agent 调用”解耦。
* **优势**：未来可轻松接入 Jira、Trello 或多维表格，而无需修改 Agent 逻辑。

---

## 3. 异步处理方案 (Async/Future)

* **模式**：全面采用 **Promise/Future (asyncio)** 模式。
* **优势**：
* **非阻塞**：在处理高并发事件订阅（如机器人被拉入千人群）时不会卡顿。
* **并行化**：利用 `asyncio.gather` 同时调用多个飞书 API，极大缩短 Agent 的思考响应时间。

---

## 4. 演进路线图 (Evolution Roadmap)

我们将按阶段稳步推进，每一阶段的产出都是下一阶段的基石：

1. **阶段一：MCP 落地 (当前)**

* 完成飞书项目 API 的 OOP 封装。
* 通过 MCP 协议将封装好的方法暴露为 LLM Tool。

2. **阶段二：Workflow 编排 (中期)**

* 将原子化的 Tool 引入工作流引擎（如 LangGraph）。
* 实现具有确定逻辑的多步自动化任务（如：自动催办延期任务）。

3. **阶段三：Autonomous Agent (终极)**

* 赋予 AI 自主推理能力。
* Agent 根据用户自然语言意图，自主组合并调用 Provider 库中的工具。

---

## 5. 工程化标准

* **代码风格**：强类型注解 (Type Hints) + 详细的 Docstring（作为 LLM 的说明书）。
* **部署配置**：Dockerfile 配合环境变量管理，支持“开发/生产”多环境切换。
* **错误处理**：将 SDK 底层错误转化为 Agent 可理解的业务提示语。

---