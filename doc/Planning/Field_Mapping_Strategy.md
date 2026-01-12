# Stage 1.5: Field Mapping & Metadata Strategy

## 1. 背景 (Context)
飞书项目 (Feishu Project) 的核心数据结构是高度自定义的。
*   **System Fields**: 标准字段（如 `name`, `created_at`）有固定的 key。
*   **Custom Fields**: 用户自定义字段使用随机生成的 ID（如 `field_192kasd`）。
*   **Problem**: Agent 如果只看到 `field_192kasd: "High"`, 无法理解这是“优先级”。

## 2. 目标 (Goal)
实现一套自动化的**元数据缓存与映射机制** (Metadata Cache & Mapping)。

## 3. 设计方案 (Design)

### 3.1 核心组件

*   **`FieldMappingService`**:
    *   **职责**: 负责从飞书 API 获取项目的“工作项类型定义” (WorkItem Type Definition)。
    *   **缓存**: 由于字段定义不常变更，应在内存中缓存（TTL 1小时）。
    *   **接口**: `get_field_name(project_key, field_key) -> str`

### 3.2 数据流

1.  Agent 请求 "获取所有 bug"。
2.  `ProjectItemProvider` 获取原始数据。
3.  `ProjectItemProvider` 调用 `FieldMappingService`。
4.  Service 检查缓存，如果无，调用 `GET /open_api/:project_key/work_item/type` 获取定义。
5.  Service 建立映射表 `{'field_192kasd': 'priority'}`。
6.  `ProjectItemProvider` 将数据清洗为 `{"priority": "High"}` 返回给 Agent。

### 3.3 新增文件

*   `src/core/cache.py`: 简单的内存缓存实现。
*   `src/providers/project/metadata.py`: 负责调用元数据 API。
*   `tests/providers/project/test_metadata.py`: 测试用例。

## 4. API 依赖

需要查阅飞书文档，找到 **"获取工作项类型详情"** 或 **"获取项目下所有字段定义"** 的 API。
通常是: `POST /open_api/:project_key/work_item/type/filter` 或类似接口。

## 5. 开发任务 (Todos)

1.  [x] 调研并确认获取字段定义的 API 路径。
2.  [x] 实现 `SimpleCache` (src/core/cache.py)。
3.  [x] 实现 `FieldMetadataProvider` (src/providers/project/metadata.py)。
4.  [x] 集成到 `ProjectManager` 中，实现自动翻译。
