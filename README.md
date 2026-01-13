# Feishu Agent (MCP Server)

[![CI](https://github.com/Wulnut/feishu_agent/actions/workflows/ci.yml/badge.svg)](https://github.com/Wulnut/feishu_agent/actions/workflows/ci.yml)

这是一个基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 构建的飞书 (Lark/Feishu) 智能代理服务。它允许 LLM (如 Claude, Cursor) 通过标准协议直接调用飞书项目 (Feishu Project) 和飞书开放平台的能力。

## ✨ 功能特性

*   **MCP 协议支持**: 基于 `FastMCP` 实现，支持标准 MCP 工具调用。
*   **飞书项目集成**:
    *   创建/更新/删除工作项 (Tasks/Issues/Bugs)。
    *   高级过滤查询（按状态、优先级、负责人）。
    *   获取字段可用选项。
*   **架构设计**:
    *   **Async First**: 全异步架构，基于 `asyncio` 和 `httpx`。
    *   **Provider 模式**: 业务逻辑与底层 API 解耦。
    *   **自动重试**: 网络错误和 5xx 服务端错误自动重试。
    *   **零硬编码**: 所有字段 Key/Value 通过名称动态解析。

## 🛠️ 可用工具 (MCP Tools)

| 工具名 | 功能描述 | 示例用法 |
|--------|---------|---------|
| `create_task` | 创建新的工作项 | "帮我创建一个 P0 优先级的 Bug：登录页面崩溃" |
| `get_active_tasks` | 获取活跃的工作项（未完成状态） | "查看当前有哪些进行中的任务" |
| `filter_tasks` | 高级过滤查询 | "找出所有张三负责的 P0 任务" |
| `update_task` | 更新工作项 | "把任务 12345 的状态改为已完成" |
| `get_task_options` | 获取字段可用选项 | "状态字段有哪些可选值？" |

### 工具详细说明

#### 1. create_task - 创建工作项

```
参数:
  - project_key: 项目空间 Key (必填)
  - name: 工作项标题 (必填)
  - priority: 优先级，可选 P0/P1/P2/P3，默认 P2
  - description: 描述
  - assignee: 负责人（姓名或邮箱）

返回: 创建成功的 Issue ID
```

**使用示例：**
```
用户: 帮我在 project_xxx 创建一个任务"修复首页加载慢的问题"，优先级 P1，指派给张三
AI: 调用 create_task(project_key="project_xxx", name="修复首页加载慢的问题", priority="P1", assignee="张三")
```

#### 2. get_active_tasks - 获取活跃任务

```
参数:
  - project_key: 项目空间 Key (必填)
  - page_size: 返回数量，默认 20，最大 100

返回: JSON 格式的工作项列表
```

**使用示例：**
```
用户: 看看 project_xxx 里有哪些正在进行的任务
AI: 调用 get_active_tasks(project_key="project_xxx")
```

#### 3. filter_tasks - 高级过滤查询

```
参数:
  - project_key: 项目空间 Key (必填)
  - status: 状态过滤，多个用逗号分隔，如 "待处理,进行中"
  - priority: 优先级过滤，多个用逗号分隔，如 "P0,P1"
  - owner: 负责人过滤（姓名或邮箱）
  - page_num: 页码，从 1 开始
  - page_size: 每页数量，默认 20

返回: JSON 格式的过滤结果
```

**使用示例：**
```
用户: 找出所有 P0 优先级的待处理任务
AI: 调用 filter_tasks(project_key="project_xxx", status="待处理", priority="P0")

用户: 李四负责的进行中任务有哪些
AI: 调用 filter_tasks(project_key="project_xxx", status="进行中", owner="李四")
```

#### 4. update_task - 更新工作项

```
参数:
  - project_key: 项目空间 Key (必填)
  - issue_id: 工作项 ID (必填)
  - name: 新标题
  - priority: 新优先级
  - description: 新描述
  - status: 新状态
  - assignee: 新负责人

返回: 更新成功消息
```

**使用示例：**
```
用户: 把任务 12345 的状态改为已完成
AI: 调用 update_task(project_key="project_xxx", issue_id=12345, status="已完成")

用户: 把任务 12345 的优先级提升到 P0，并转给王五
AI: 调用 update_task(project_key="project_xxx", issue_id=12345, priority="P0", assignee="王五")
```

#### 5. get_task_options - 获取字段可用选项

```
参数:
  - project_key: 项目空间 Key (必填)
  - field_name: 字段名称，如 "status", "priority"

返回: JSON 格式的选项列表
```

**使用示例：**
```
用户: 状态字段有哪些可选值
AI: 调用 get_task_options(project_key="project_xxx", field_name="status")
返回: {"field": "status", "options": {"待处理": "opt_1", "进行中": "opt_2", "已完成": "opt_3"}}
```

## 🚀 快速开始

### 方式一：通过 uv tool install（推荐，最简单）

```bash
# 安装
uv tool install --from git+https://github.com/Wulnut/feishu_agent feishu-agent

# 运行
feishu-agent
```

安装后，`feishu-agent` 命令会自动添加到 PATH 中，可以直接使用。

### 方式二：从源码运行（开发模式）

#### 前置要求

*   [uv](https://github.com/astral-sh/uv) (推荐) 或 Python 3.11+
*   Docker (可选，用于容器化开发)

#### 1. 克隆仓库

```bash
git clone https://github.com/Wulnut/feishu_agent.git
cd feishu_agent
```

#### 2. 环境配置

创建 `.env` 文件并填写您的飞书凭证：

```bash
# 创建 .env 文件
cat > .env << EOF
LARK_APP_ID=your_app_id
LARK_APP_SECRET=your_app_secret
FEISHU_PROJECT_USER_TOKEN=your_token
FEISHU_PROJECT_USER_KEY=your_user_key
# 或使用 Plugin 方式（推荐）
# FEISHU_PROJECT_PLUGIN_ID=your_plugin_id
# FEISHU_PROJECT_PLUGIN_SECRET=your_plugin_secret
EOF
```

#### 3. 安装依赖

```bash
uv sync
```

#### 4. 启动服务

```bash
uv run main.py
```

服务启动后，将通过 `stdio` (标准输入输出) 进行通信。日志会输出到 `log/agent.log` 文件中。

可以使用 `tail -f log/agent.log` 实时查看运行日志。

## 🔌 MCP 客户端配置

### Cursor IDE 配置

在 Cursor 中配置 MCP server，编辑 `~/.cursor/mcp.json`（Linux/macOS）或 `%APPDATA%\Cursor\mcp.json`（Windows）。

**如果使用 `uv tool install` 安装（推荐）：**
```json
{
  "mcpServers": {
    "feishu-agent": {
      "command": "feishu-agent"
    }
  }
}
```

**如果从源码运行：**
```json
{
  "mcpServers": {
    "feishu-agent": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/feishu_agent",
        "main.py"
      ]
    }
  }
}
```

**配置说明：**
*   推荐使用 `uv tool install` 方式，配置更简单
*   如果从源码运行，需要确保 `uv` 已安装并在系统 PATH 中
*   确保 `.env` 文件已正确配置飞书凭证（或设置环境变量）
*   配置修改后需要重启 Cursor 才能生效

### Claude Desktop 配置

在 Claude Desktop 中配置，编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`（macOS）或 `%APPDATA%\Claude\claude_desktop_config.json`（Windows）：

```json
{
  "mcpServers": {
    "feishu-agent": {
      "command": "feishu-agent"
    }
  }
}

{
  "mcpServers": {
    "feishu-agent": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/path/to/feishu_agent",
        "main.py"
      ]
    }
  }
}
```

**注意**：使用 `uv tool install` 安装后，需要确保 `~/.local/bin`（Linux/macOS）或 `%USERPROFILE%\.local\bin`（Windows）在 PATH 中。

### 使用方式

配置完成后，在 Cursor 或 Claude Desktop 中可以直接通过自然语言调用飞书项目相关功能，例如：

*   "查询我的活跃工作项"
*   "创建一个 P0 的紧急 Bug"
*   "查看项目中所有待处理的任务"
*   "把任务 12345 标记为已完成"
*   "找出张三负责的所有 P0 任务"

MCP server 会自动处理这些请求并调用相应的飞书 API。

## 🧪 测试 (Testing)

本项目严格遵循 **TDD (测试驱动开发)** 流程。

运行所有测试：
```bash
uv run pytest
```

运行特定模块测试：
```bash
uv run pytest tests/providers/project/test_work_item_provider.py -v
```

查看测试覆盖率：
```bash
uv run pytest tests/ -v --tb=short
```

测试环境说明：
*   使用 `pytest-asyncio` 处理异步测试。
*   使用 `respx` 模拟 HTTP 请求，无需真实 Token 即可运行单元测试。
*   当前测试覆盖：**135 个测试用例全部通过**。

## 🐳 部署 (Deployment)

### 使用 Docker

1. **构建镜像**
   ```bash
   docker compose build
   ```

2. **启动服务**
   ```bash
   docker compose up -d
   ```

或者直接使用 `Dockerfile`:
```bash
docker build -t feishu-agent .
docker run --env-file .env feishu-agent
```

## 📂 项目结构

```text
.
├── src/
│   ├── core/               # 核心组件
│   │   ├── auth.py         # 认证管理
│   │   ├── cache.py        # 缓存工具
│   │   ├── config.py       # 配置管理
│   │   └── project_client.py # HTTP 客户端（含重试机制）
│   ├── providers/          # 能力层 (Provider 模式)
│   │   └── project/
│   │       ├── api/        # 原子 API 封装
│   │       ├── managers/   # 元数据管理器
│   │       └── work_item_provider.py # 业务逻辑编排
│   ├── schemas/            # Pydantic 数据模型
│   │   └── project.py      # 工作项相关模型
│   ├── services/           # 服务层
│   └── mcp_server.py       # MCP 工具定义
├── tests/                  # 测试用例 (135+)
├── main.py                 # 程序入口
├── pyproject.toml          # 依赖配置
└── doc/                    # 详细开发文档
```

## 📏 开发规范

在贡献代码前，请务必阅读以下文档：

1.  **[开发协议 (Development Protocol)](doc/Planning/First_stage/Development_Protocol.md)**: 规定了 Bottom-Up 开发流程和 TDD 测试规范。
2.  **[API 参考文档](doc/Feishu_project_api/API_Reference.md)**: 飞书项目 API 的详细说明。
3.  **[项目进度](doc/Planning/Progress.md)**: 当前开发进度和路线图。

### 核心原则
*   **异步优先**: 所有 I/O 操作必须使用 `async/await`。
*   **类型安全**: 严格使用 Python Type Hints。
*   **零硬编码**: 所有 Key/Value 通过 MetadataManager 动态解析。
*   **错误处理**: 在 Provider 层捕获底层 API 异常，返回对 Agent 友好的错误信息。
*   **自动重试**: 网络错误和 5xx 错误自动重试（最多 3 次，指数退避）。
