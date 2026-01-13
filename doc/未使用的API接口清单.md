# 飞书项目 MCP 未使用的 API 接口清单

## 当前已实现的 MCP 工具

1. ✅ `list_projects` - 列出所有项目空间
2. ✅ `create_task` - 创建工作项
3. ✅ `get_tasks` - 获取工作项列表（支持过滤）
4. ✅ `filter_tasks` - 高级过滤查询
5. ✅ `update_task` - 更新工作项
6. ✅ `get_task_options` - 获取字段选项

---

## 未使用的 API 接口

### 1. 工作项相关 (WorkItemAPI)

#### 1.1 `query` - 批量获取工作项详情
- **API**: `POST /open_api/{project_key}/work_item/{work_item_type_key}/query`
- **功能**: 根据工作项 ID 列表批量获取详细信息
- **用途**: 获取特定工作项的完整信息（包括所有字段值）
- **优先级**: ⭐⭐⭐⭐⭐ (高 - 查看任务详情常用)

#### 1.2 `delete` - 删除工作项
- **API**: `DELETE /open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}`
- **功能**: 删除指定的工作项
- **用途**: 清理不需要的任务
- **优先级**: ⭐⭐⭐ (中 - 谨慎使用)

#### 1.3 `batch_update` - 批量更新工作项
- **API**: `POST /open_api/work_item/batch_update`
- **功能**: 批量更新多个工作项的同一字段
- **用途**: 批量修改优先级、状态等
- **优先级**: ⭐⭐⭐⭐ (中高 - 批量操作有用)

#### 1.4 `get_create_meta` - 获取创建工作项元数据
- **API**: `GET /open_api/{project_key}/work_item/{work_item_type_key}/meta`
- **功能**: 获取创建工作项时需要的字段信息、必填项、选项等
- **用途**: 在创建任务前了解需要填写哪些字段
- **优先级**: ⭐⭐⭐⭐ (中高 - 创建任务前很有用)

---

### 2. 项目空间相关 (ProjectAPI)

#### 2.1 `get_project_details` - 获取空间详情
- **API**: `POST /open_api/projects/detail`
- **功能**: 获取项目空间的详细信息（名称、简称、配置等）
- **用途**: 查看项目空间的详细信息
- **优先级**: ⭐⭐ (低 - 信息查询)

---

### 3. 元数据配置相关 (MetadataAPI)

#### 3.1 `get_business_lines` - 获取业务线详情
- **API**: `GET /open_api/{project_key}/business/all`
- **功能**: 获取项目空间下的业务线列表
- **用途**: 了解项目的业务线结构
- **优先级**: ⭐⭐ (低 - 配置查询)

#### 3.2 `get_work_item_type_config` - 获取工作项类型配置
- **API**: `GET /open_api/{project_key}/work_item/type/{work_item_type_key}`
- **功能**: 获取工作项类型的基础配置信息
- **用途**: 了解工作项类型的配置详情
- **优先级**: ⭐⭐⭐ (中 - 配置查询)

#### 3.3 `get_workflow_templates` - 获取流程模板列表
- **API**: `GET /open_api/{project_key}/template_list/{work_item_type_key}`
- **功能**: 获取工作项类型下的流程模板列表
- **用途**: 查看可用的流程模板
- **优先级**: ⭐⭐ (低 - 配置查询)

---

### 4. 字段配置相关 (FieldAPI)

#### 4.1 `create_field` - 创建自定义字段
- **API**: `POST /open_api/{project_key}/field/{work_item_type_key}/create`
- **功能**: 为工作项类型创建自定义字段
- **用途**: 扩展工作项的字段
- **优先级**: ⭐⭐ (低 - 配置管理，需要权限)

#### 4.2 `update_field` - 更新自定义字段
- **API**: `PUT /open_api/{project_key}/field/{work_item_type_key}`
- **功能**: 更新自定义字段的配置
- **用途**: 修改字段配置
- **优先级**: ⭐⭐ (低 - 配置管理，需要权限)

#### 4.3 `get_work_item_relations` - 获取工作项关系列表
- **API**: `GET /open_api/{project_key}/work_item/relation`
- **功能**: 获取工作项之间的关系类型配置
- **用途**: 了解工作项可以建立哪些关系（关联、依赖等）
- **优先级**: ⭐⭐⭐ (中 - 关系管理)

---

### 5. 用户相关 (UserAPI)

#### 5.1 `get_team_members` - 获取团队成员
- **API**: `GET /open_api/{project_key}/teams/all`
- **功能**: 获取项目空间下的所有团队成员
- **用途**: 查看项目成员列表
- **优先级**: ⭐⭐⭐ (中 - 成员管理)

#### 5.2 `query_users` - 获取用户详情
- **API**: `POST /open_api/user/query`
- **功能**: 根据 user_key、email 等查询用户详细信息
- **用途**: 获取用户的详细信息
- **优先级**: ⭐⭐⭐ (中 - 用户信息查询)

#### 5.3 `search_users` - 搜索用户
- **API**: `POST /open_api/user/search`
- **功能**: 在租户内搜索用户（支持用户名、邮箱等）
- **用途**: 查找用户
- **优先级**: ⭐⭐⭐⭐ (中高 - 分配任务时有用)

#### 5.4 `get_user_group_members` - 查询用户组成员
- **API**: `POST /open_api/{project_key}/user_groups/members/page`
- **功能**: 查询用户组的成员列表
- **用途**: 查看用户组成员
- **优先级**: ⭐⭐ (低 - 用户组管理)

#### 5.5 `create_user_group` - 创建自定义用户组
- **API**: `POST /open_api/{project_key}/user_group`
- **功能**: 创建自定义用户组
- **用途**: 创建用户组
- **优先级**: ⭐⭐ (低 - 配置管理，需要权限)

---

## 推荐优先实现的接口

### 高优先级 (⭐⭐⭐⭐⭐)
1. **`query` - 批量获取工作项详情**
   - 理由: 查看任务详情是最常用的功能之一
   - 建议工具名: `get_task_details` 或 `get_task`

### 中高优先级 (⭐⭐⭐⭐)
2. **`get_create_meta` - 获取创建工作项元数据**
   - 理由: 创建任务前了解字段要求很有用
   - 建议工具名: `get_create_task_meta`

3. **`search_users` - 搜索用户**
   - 理由: 分配任务时需要查找用户
   - 建议工具名: `search_users`

4. **`batch_update` - 批量更新工作项**
   - 理由: 批量操作可以提高效率
   - 建议工具名: `batch_update_tasks`

### 中优先级 (⭐⭐⭐)
5. **`get_team_members` - 获取团队成员**
   - 建议工具名: `get_team_members`

6. **`get_work_item_relations` - 获取工作项关系列表**
   - 建议工具名: `get_task_relations`

7. **`get_work_item_type_config` - 获取工作项类型配置**
   - 建议工具名: `get_task_type_config`

---

## 注意事项

1. **删除操作**: `delete` 接口需要谨慎实现，建议添加确认机制
2. **权限要求**: 字段和用户组的创建/更新需要管理员权限
3. **批量操作**: `batch_update` 目前 API 限制每次只能更新一个字段
4. **内部使用**: 部分接口（如 `get_work_item_types`、`get_all_fields`）已在内部使用，但未暴露为 MCP 工具
