# 第一阶段概览

## 1. 开发环境与核心库 (The Tech Stack)

| 类别 | 推荐组件 | 说明 |
| --- | --- | --- |
| **基础运行环境** | **Python 3.11.x** | 兼顾性能与 `asyncio` 稳定性。 |
| **依赖管理工具** | **uv** | 替代 pip，管理虚拟环境并锁定 `uv.lock` 以保证 Docker 构建一致性。 |
| **飞书底层通信** | **`lark-oapi`** | 官方 SDK，负责鉴权、自动重试及原生异步接口。 |
| **MCP 实现框架** | **`FastMCP` (python-mcp)** | 类似 FastAPI 的装饰器风格，极大简化工具注册过程。 |
| **配置与校验** | **`pydantic-settings`** | 基于 Pydantic v2，严格校验 `.env` 环境变量中的 AppID/Secret。 |

---

## 2. 方法库（Modules）逻辑划分

按照你的需求，我们将方法库分为三级，确保“飞书通用”与“飞书项目”解耦。

#### **A. 基础支持库 (Core Methods)**

* **`AuthManager` (单例)**：处理 `tenant_access_token`。飞书项目的 API 有时需要特殊的 `project_token` 或 `user_token`，该库负责根据调用上下文自动切换。
* **`AsyncHttpClient`**：封装 `lark-oapi` 的异步 Request 模板，统一处理请求超时和错误捕获（Error Handling）。

#### **B. 通用方法库 (Common Library - `tools/common`)**

这些是 Agent 未来的“手脚”，负责跨项目的通用操作：

* **`IMProvider`**：发送富文本消息、卡片消息、上传文件。
* **`BaseProvider`**：对多维表格进行 CRUD 操作（未来扩展用）。

#### **C. 飞书项目专用库 (Project Library - `tools/project`)**

这是你当前的核心，建议按功能逻辑细分为以下方法集：

* **`WorkItemProvider`**：工作项（任务、需求、缺陷）的查询、创建、修改。
* **`GanttProvider`**：处理排期数据、里程碑信息。
* **`FieldMapping`**：专门处理“自定义字段”的映射（飞书项目大量使用 `field_123` 这种 ID，需要一个方法将其映射为“负责人”或“优先级”）。

---

## 3. 第一阶段目录结构（实战版）

```text
lark_mcp_stage1/
├── .env                # 存放 LARK_APP_ID, LARK_APP_SECRET
├── .python-version     # uv 自动识别版本 (3.11)
├── pyproject.toml      # 项目元数据与依赖
├── main.py             # MCP Server 入口 (FastMCP)
├── src/
│   ├── core/
│   │   ├── client.py   # 异步 LarkClient 封装
│   │   └── config.py   # Pydantic Settings
│   ├── providers/      # 能力者目录
│   │   ├── base.py     # 抽象基类 (Abstract Base Class)
│   │   ├── common_im.py# 通用消息库
│   │   └── project/    # 飞书项目方法库
│   │       ├── items.py# 工作项操作
│   │       └── utils.py# 字段映射工具
│   └── schemas/        # 定义 Agent 返回的简洁数据格式

```

---

## 4. 关键代码模式示例 (Future/Promise 风格)

在 `src/providers/project/items.py` 中，我们会这样组织方法：

```python
from typing import List, Dict
from src.core.client import get_lark_client

class ProjectItemProvider:
    def __init__(self, project_key: str):
        self.project_key = project_key
        self.client = get_lark_client()

    async def fetch_active_tasks(self) -> List[Dict]:
        """
        [Future 模式] 异步获取所有进行中的任务
        """
        # 1. 构造异步 Future
        request = (
            lark.api.project.v1.ListWorkItemRequest.builder()
            .project_key(self.project_key)
            .query('{"status_type": "in_progress"}')
            .build()
        )

        # 2. 等待结果 (Promise Resolved)
        response = await self.client.project.v1.work_item.alist(request)

        # 3. 数据清洗：只给 Agent 返回它关心的字段，减少 Token 消耗
        return [{"id": i.id, "name": i.name} for i in response.data.items]

```

---

## 5. Docker 基础镜像选择

我们将使用基于 **Debian Bookworm** 的 Python 3.11 镜像，因为它对各种 C 扩展（如果未来需要向量库）支持更好：

```dockerfile
FROM python:3.11-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
# 后续安装与运行指令...

```
---