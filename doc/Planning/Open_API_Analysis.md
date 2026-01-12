# Feishu Project Open API Analysis (Postman Template Based)

This document summarizes the key findings from the official Feishu Project Open API Postman Collection to guide the development of the MCP Agent.

## 1. Authentication & Base Config

*   **Base URL**: `https://project.feishu.cn` (Adjustable via `.env`)
*   **Headers**:
    *   `X-PLUGIN-TOKEN`: Required for all calls.
    *   `X-USER-KEY`: Required if using plugin-level token to identify the operator.
    *   `Content-Type`: `application/json`.

## 2. Meta-data & Schema APIs

These APIs are critical for the **Field Mapping** strategy.

### 2.1 Get All Fields
*   **Endpoint**: `POST /open_api/:project_key/field/all`
*   **Purpose**: Get the definition of all fields in a project.
*   **Payload**:
    ```json
    {
      "work_item_type_key": "story" // Optional
    }
    ```
*   **Key Response Fields**:
    *   `field_key`: e.g., `field_123456`
    *   `field_name`: e.g., "Priority"
    *   `field_type_key`: e.g., `single_select`, `text`, `user`
    *   `options`: List of `{ "label": "...", "value": "..." }` for select fields.

### 2.2 Get Work Item Types
*   **Endpoint**: `GET /open_api/:project_key/work_item/all-types`
*   **Purpose**: List all work item types (e.g., bug, story, task) available in the project.

## 3. Work Item Operations

### 3.1 Filtering (Querying)
*   **Single Project**: `POST /open_api/:project_key/work_item/filter`
*   **Cross Project**: `POST /open_api/work_items/filter_across_project`
*   **Search with Params**: `POST /open_api/:project_key/work_item/:work_item_type_key/search/params`
    *   Supports `search_group` with `conjunction` (AND/OR).
    *   Supports `fields` selection (decides which fields are returned).

### 3.2 Read/Write
*   **Detail**: `POST /open_api/:project_key/work_item/:work_item_type_key/query` (Pass `work_item_ids`).
*   **Create**: `POST /open_api/:project_key/work_item/create`.
*   **Update**: `PUT /open_api/:project_key/work_item/:work_item_type_key/:work_item_id`.

## 4. Development Guidance for Field Mapping

To implement the "Human Readable Fields" feature:

1.  **Cache the Mapping**:
    *   When `ProjectManager` is initialized for a `project_key`, it should call `/open_api/:project_key/field/all`.
    *   Build two maps:
        *   `key_to_name`: `{"field_123": "Priority"}`
        *   `name_to_key`: `{"Priority": "field_123"}` (Useful for creating/updating).
2.  **Translate on Retrieval**:
    *   Iterate through work item `field_value_pairs` or the root JSON object.
    *   Replace `field_xxx` keys with their human names before returning to the Agent.
3.  **Translate on Submission**:
    *   When an Agent says "Set priority to High", the provider should look up "Priority" in the `name_to_key` map to get `field_123`.

## 5. Next Implementation Steps

1.  **Add `FieldDefinition` Schema** to `src/schemas/project.py`.
2.  **Implement `WorkItemAPI.get_project_fields()`** in `src/providers/project/api.py`.
3.  **Create `src/providers/project/metadata.py`** to manage the mapping logic and caching.
4.  **Update `src/providers/project/manager.py`** to use the metadata service.
