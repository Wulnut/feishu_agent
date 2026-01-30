import logging
import re
from typing import Dict, List, Optional

from src.core.project_client import get_project_client

logger = logging.getLogger(__name__)

# 安全校验：project_key 和 type_key 的合法字符白名单
# 仅允许字母、数字、下划线和连字符
_SAFE_KEY_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


def _validate_key(key: str, key_name: str) -> None:
    """
    校验 key 是否符合安全规范（防止路径遍历攻击）

    Args:
        key: 待校验的 key 值
        key_name: key 的名称（用于错误提示）

    Raises:
        ValueError: 当 key 包含非法字符时
    """
    if not key:
        raise ValueError(f"{key_name} 不能为空")
    if not _SAFE_KEY_PATTERN.match(key):
        raise ValueError(
            f"{key_name} 包含非法字符，仅允许字母、数字、下划线和连字符: {key[:20]}..."
        )


def _mask_sensitive(value: str, visible_chars: int = 4) -> str:
    """对敏感信息进行脱敏处理，仅显示前几个字符"""
    if not value or len(value) <= visible_chars:
        return "***"
    return f"{value[:visible_chars]}***"


def _mask_project_key(project_key: str) -> str:
    """对 project_key 进行脱敏"""
    if not project_key:
        return "***"
    # project_key 格式通常为 "project_xxx"，保留前缀
    if project_key.startswith("project_"):
        return (
            f"project_{project_key[8:12]}***"
            if len(project_key) > 12
            else "project_***"
        )
    return _mask_sensitive(project_key)


class WorkItemAPI:
    """
    飞书项目工作项 API 封装 (Data Layer)
    只负责底层 HTTP 调用，不含业务逻辑
    """

    def __init__(self):
        self.client = get_project_client()

    def _validate_keys(self, project_key: str, work_item_type_key: str = None) -> None:
        """校验所有 key 参数的安全性"""
        _validate_key(project_key, "project_key")
        if work_item_type_key:
            _validate_key(work_item_type_key, "work_item_type_key")

    async def create(
        self,
        project_key: str,
        work_item_type_key: str,
        name: str,
        field_value_pairs: List[Dict],
        template_id: Optional[int] = None,
    ) -> int:
        """创建工作项"""
        # 安全校验
        self._validate_keys(project_key, work_item_type_key)
        # 日志脱敏：不记录完整的 project_key 和任务名称
        logger.info(
            "Creating work item: project_key=%s, type_key=%s, name_len=%d",
            _mask_project_key(project_key),
            work_item_type_key,
            len(name) if name else 0,
        )
        # DEBUG 级别也进行脱敏，仅记录字段数量而非内容
        logger.debug("Field value pairs count: %d", len(field_value_pairs))

        url = f"/open_api/{project_key}/work_item/create"
        payload = {
            "work_item_type_key": work_item_type_key,
            "name": name,
            "field_value_pairs": field_value_pairs,
        }
        if template_id:
            payload["template_id"] = template_id
            logger.debug("Using template_id=%d", template_id)

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "Create WorkItem failed: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"Create WorkItem failed: {err_msg}")

        issue_id = data.get("data")
        logger.info("Work item created successfully: issue_id=%s", issue_id)
        return issue_id

    async def query(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_ids: List[int],
        expand: Optional[Dict] = None,
    ) -> List[Dict]:
        """批量获取工作项详情"""
        self._validate_keys(project_key, work_item_type_key)
        logger.debug(
            "Querying work items: project_key=%s, type_key=%s, ids_count=%d",
            _mask_project_key(project_key),
            work_item_type_key,
            len(work_item_ids),
        )

        url = f"/open_api/{project_key}/work_item/{work_item_type_key}/query"
        payload = {"work_item_ids": work_item_ids, "expand": expand or {}}
        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "Query WorkItem failed: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"Query WorkItem failed: {err_msg}")

        items = data.get("data", [])
        logger.info("Query successful: retrieved %d work items", len(items))
        return items

    async def update(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
        update_fields: List[Dict],
    ) -> None:
        """更新工作项"""
        self._validate_keys(project_key, work_item_type_key)
        logger.info(
            "Updating work item: project_key=%s, type_key=%s, id=%s",
            _mask_project_key(project_key),
            work_item_type_key,
            work_item_id,
        )
        # 仅记录更新字段数量，不记录具体内容
        logger.debug("Update fields count: %d", len(update_fields))

        url = f"/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}"
        payload = {"update_fields": update_fields}
        resp = await self.client.put(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "Update WorkItem failed: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"Update WorkItem failed: {err_msg}")

        logger.info("Work item updated successfully: id=%s", work_item_id)

    async def delete(
        self, project_key: str, work_item_type_key: str, work_item_id: int
    ) -> None:
        """删除工作项"""
        self._validate_keys(project_key, work_item_type_key)
        logger.warning(
            "Deleting work item: project_key=%s, type_key=%s, id=%s",
            _mask_project_key(project_key),
            work_item_type_key,
            work_item_id,
        )

        url = f"/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}"
        resp = await self.client.delete(url)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "Delete WorkItem failed: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"Delete WorkItem failed: {err_msg}")

        logger.info("Work item deleted successfully: id=%s", work_item_id)

    async def filter(
        self,
        project_key: str,
        work_item_type_keys: List[str],
        page_num: int = 1,
        page_size: int = 20,
        expand: Optional[Dict] = None,
        **kwargs,
    ) -> Dict:
        """基础筛选"""
        # 安全校验
        _validate_key(project_key, "project_key")
        for type_key in work_item_type_keys:
            _validate_key(type_key, "work_item_type_key")
        logger.debug(
            "Filtering work items: project_key=%s, type_keys=%s, page=%d/%d",
            _mask_project_key(project_key),
            work_item_type_keys,
            page_num,
            page_size,
        )
        # 仅记录过滤条件的键，不记录值
        logger.debug("Filter kwargs keys: %s", list(kwargs.keys()))

        url = f"/open_api/{project_key}/work_item/filter"
        payload = {
            "work_item_type_keys": work_item_type_keys,
            "page_num": page_num,
            "page_size": page_size,
            "expand": expand or {},
            **kwargs,
        }
        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "Filter WorkItem failed: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"Filter WorkItem failed: {err_msg}")

        result = data.get("data", {})
        # 处理返回格式：可能是 list 或 dict
        if isinstance(result, list):
            items_count = len(result)
            logger.info(
                "Filter successful: retrieved %d items (list format)", items_count
            )
            # 包装 list 为标准字典格式
            return {"work_items": result, "total": items_count, "pagination": {}}
        elif isinstance(result, dict):
            items_count = len(result.get("work_items", []))
            logger.info(
                "Filter successful: retrieved %d items (dict format)", items_count
            )
            return result
        else:
            logger.warning(f"Unexpected result format: {type(result)}")
            return {"work_items": [], "total": 0, "pagination": {}}

    async def search_params(
        self,
        project_key: str,
        work_item_type_key: str,
        search_group: Dict,
        page_num: int = 1,
        page_size: int = 20,
        fields: Optional[List[str]] = None,
    ) -> Dict:
        """复杂条件搜索"""
        self._validate_keys(project_key, work_item_type_key)
        logger.debug(
            "Searching work items with params: project_key=%s, type_key=%s, page=%d/%d",
            _mask_project_key(project_key),
            work_item_type_key,
            page_num,
            page_size,
        )
        # 仅记录搜索条件结构，不记录具体值
        logger.debug(
            "Search group keys: %s", list(search_group.keys()) if search_group else []
        )

        url = f"/open_api/{project_key}/work_item/{work_item_type_key}/search/params"
        payload = {
            "search_group": search_group,
            "page_num": page_num,
            "page_size": page_size,
        }
        if fields:
            payload["fields"] = fields
            logger.debug("Requested fields: %s", fields)

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "Search Params failed: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"Search Params failed: {err_msg}")

        result = data.get("data", {})
        # 兼容不同的 API 返回格式: data 可能是 dict 或 list
        if isinstance(result, list):
            # 如果 data 是 list，则直接作为 work_items
            result = {"work_items": result, "total": len(result)}
        items_count = len(result.get("work_items", []))
        logger.info("Search successful: retrieved %d items", items_count)
        return result

    async def batch_update(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_ids: List[int],
        update_fields: List[Dict],
    ) -> str:
        """批量更新工作项的单个字段。

        飞书 API 限制：每次请求仅能更新一个字段。
        多字段更新需由上层业务拆分为多次调用。

        API: POST /open_api/work_item/batch_update

        Args:
            project_key: 项目 Key。
            work_item_type_key: 工作项类型 Key。
            work_item_ids: 要更新的工作项 ID 列表。
            update_fields: 字段列表（当前仅支持单元素）。
                每个元素格式: {"field_key": str, "field_value": Any}

        Returns:
            后台任务 ID（用于异步任务追踪）。

        Raises:
            NotImplementedError: 当传入多个字段时。
            RuntimeError: 当 API 返回业务错误时。
        """
        self._validate_keys(project_key, work_item_type_key)
        url = "/open_api/work_item/batch_update"

        # API 限制：单次仅支持一个字段
        if not update_fields or len(update_fields) > 1:
            raise NotImplementedError(
                "Batch update only supports single field per call"
            )

        field = update_fields[0]

        # update_mode: 0 = 覆盖原值（Replace）
        UPDATE_MODE_REPLACE = 0

        payload = {
            "project_key": project_key,
            "work_item_type_key": work_item_type_key,
            "work_item_ids": work_item_ids,
            "field_key": field["field_key"],
            "after_field_value": field["field_value"],
            "update_mode": UPDATE_MODE_REPLACE,
        }

        logger.info(
            "Batch update: project=%s, type=%s, count=%d, field=%s",
            _mask_project_key(project_key),
            work_item_type_key,
            len(work_item_ids),
            field["field_key"],
        )

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()

        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "Batch update failed: code=%s, msg=%s", data.get("err_code"), err_msg
            )
            raise RuntimeError(f"批量更新失败: {err_msg}")

        task_id = data.get("data")
        logger.info("Batch update queued: task_id=%s", task_id)
        return task_id

    async def get_create_meta(self, project_key: str, work_item_type_key: str) -> Dict:
        """获取创建工作项的元数据

        对应 Postman: 工作项 > 工作项列表 > 获取创建工作项元数据
        API: GET /open_api/:project_key/work_item/:work_item_type_key/meta

        该接口返回创建工作项时需要填写的字段信息，包括:
        - 字段列表及其配置
        - 必填字段
        - 字段选项值
        - 默认值等

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key (如 story, task, bug 等)

        Returns:
            创建工作项所需的元数据信息

        Raises:
            Exception: API 调用失败时抛出异常
        """
        self._validate_keys(project_key, work_item_type_key)
        url = f"/open_api/{project_key}/work_item/{work_item_type_key}/meta"

        logger.debug(
            "Getting create meta: project_key=%s, type_key=%s",
            _mask_project_key(project_key),
            work_item_type_key,
        )

        resp = await self.client.get(url)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "获取创建工作项元数据失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"获取创建工作项元数据失败: {err_msg}")

        meta = data.get("data", {})
        logger.debug("Retrieved create meta successfully")
        return meta

    async def search_by_relation(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
        relation_key: Optional[str] = None,
        page_num: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """
        关联工作项搜索

        对应 Postman: 工作项 > 工作项列表 > 关联工作项搜索
        API: POST /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/search_by_relation

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key
            work_item_id: 工作项 ID
            relation_key: 关联关系 Key (可选)
            page_num: 页码
            page_size: 每页数量

        Returns:
            搜索结果，包含关联的工作项列表

        Raises:
            Exception: API 调用失败时抛出异常
        """
        self._validate_keys(project_key, work_item_type_key)
        url = f"/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/search_by_relation"

        payload = {
            "page_num": page_num,
            "page_size": page_size,
        }
        if relation_key:
            payload["relation_key"] = relation_key

        logger.debug(
            "Searching by relation: project=%s, type=%s, id=%s, relation=%s",
            _mask_project_key(project_key),
            work_item_type_key,
            work_item_id,
            relation_key,
        )

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "关联工作项搜索失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"关联工作项搜索失败: {err_msg}")

        result = data.get("data", {})
        count = len(result.get("work_items", []))
        logger.info("Search by relation successful: found %d items", count)
        return result

    async def get_operate_history(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
        page_num: int = 1,
        page_size: int = 20,
    ) -> Dict:
        """
        获取工作项操作记录

        对应 Postman: 工作项 > 工作项列表 > 获取工作项操作记录
        API: GET /open_api/:project_key/work_item/:work_item_type_key/:work_item_id/operate-history

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key
            work_item_id: 工作项 ID
            page_num: 页码
            page_size: 每页数量

        Returns:
            操作记录列表

        Raises:
            Exception: API 调用失败时抛出异常
        """
        self._validate_keys(project_key, work_item_type_key)
        url = f"/open_api/{project_key}/work_item/{work_item_type_key}/{work_item_id}/operate-history"

        # GET 请求参数需要放在 params 中
        params = {
            "page_num": page_num,
            "page_size": page_size,
        }

        logger.debug(
            "Getting operate history: project=%s, type=%s, id=%s",
            _mask_project_key(project_key),
            work_item_type_key,
            work_item_id,
        )

        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "获取工作项操作记录失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"获取工作项操作记录失败: {err_msg}")

        result = data.get("data", [])
        logger.info("Retrieved %d operate history records", len(result))
        return result

    async def query_man_hour(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_ids: List[int],
    ) -> Dict:
        """
        查询工时

        对应 Postman: 工作项 > 工作项列表 > 查询工时
        API: POST /open_api/work_item/man_hour/query

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key
            work_item_ids: 工作项 ID 列表

        Returns:
            工时信息列表

        Raises:
            Exception: API 调用失败时抛出异常
        """
        self._validate_keys(project_key, work_item_type_key)
        url = "/open_api/work_item/man_hour/query"
        payload = {
            "project_key": project_key,
            "work_item_type_key": work_item_type_key,
            "work_item_ids": work_item_ids,
        }

        logger.debug(
            "Querying man hours: project=%s, type=%s, count=%d",
            _mask_project_key(project_key),
            work_item_type_key,
            len(work_item_ids),
        )

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "查询工时失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"查询工时失败: {err_msg}")

        result = data.get("data", {})
        logger.info("Man hours queried successfully")
        return result

    async def update_actual_time(
        self,
        project_key: str,
        work_item_type_key: str,
        work_item_id: int,
        actual_time: int,
    ) -> Dict:
        """
        更新实际工时

        对应 Postman: 工作项 > 工作项列表 > 更新实际工时
        API: POST /open_api/work_item/actual_time/update

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key
            work_item_id: 工作项 ID
            actual_time: 实际工时 (分钟)

        Returns:
            更新结果

        Raises:
            Exception: API 调用失败时抛出异常
        """
        self._validate_keys(project_key, work_item_type_key)
        url = "/open_api/work_item/actual_time/update"
        payload = {
            "project_key": project_key,
            "work_item_type_key": work_item_type_key,
            "work_item_id": work_item_id,
            "actual_time": actual_time,
        }

        logger.info(
            "Updating actual time: project=%s, type=%s, id=%s, time=%d",
            _mask_project_key(project_key),
            work_item_type_key,
            work_item_id,
            actual_time,
        )

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "更新实际工时失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"更新实际工时失败: {err_msg}")

        result = data.get("data", {})
        logger.info("Actual time updated successfully")
        return result
