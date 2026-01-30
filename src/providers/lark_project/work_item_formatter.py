"""
工作项格式化器 - 负责工作项数据的简化和可读化转换

职责：
- 简化工作项为摘要格式（减少 Token 消耗）
- 增强工作项数据，将 ID 转换为可读名称
- 批量处理工作项列表

设计说明：
- 依赖 MetadataManager 获取用户名和工作项名称
- 依赖 FieldResolver 进行字段值提取
- 支持新版 (fields) 和旧版 (field_value_pairs) 数据结构
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Set

from src.providers.lark_project.managers import MetadataManager
from src.providers.lark_project.field_resolver import FieldResolver

logger = logging.getLogger(__name__)


class WorkItemFormatter:
    """
    工作项格式化器

    提供工作项数据简化和可读化转换的统一接口。

    Attributes:
        meta: MetadataManager 实例
        field_resolver: FieldResolver 实例
    """

    # 缓存中"未找到"的标记值
    _NOT_FOUND_MARKER: str = "__NOT_FOUND__"

    def __init__(
        self,
        meta: MetadataManager,
        field_resolver: FieldResolver,
        work_item_cache: Optional[Any] = None,
    ):
        """
        初始化工作项格式化器

        Args:
            meta: MetadataManager 实例
            field_resolver: FieldResolver 实例
            work_item_cache: 工作项缓存（可选）
        """
        self.meta = meta
        self.field_resolver = field_resolver
        self._work_item_cache = work_item_cache

    async def simplify_work_item(
        self, item: Dict[str, Any], field_mapping: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        将工作项简化为摘要格式，减少 Token 消耗

        Args:
            item: 原始工作项字典
            field_mapping: 字段名称到字段Key的映射（可选）

        Returns:
            简化后的工作项字典，包含 id, name, status, priority, owner
        """

        def get_field_key(field_name: str) -> str:
            if field_mapping and field_name in field_mapping:
                return field_mapping[field_name]
            return field_name

        priority_key = get_field_key("priority")
        priority_raw = FieldResolver.extract_field_value(item, priority_key)
        # 脱敏处理：截断优先级值
        priority_value = priority_raw[:20] if priority_raw else None

        return {
            "id": item.get("id"),
            "name": item.get("name"),
            "status": FieldResolver.extract_field_value(item, get_field_key("status")),
            "priority": priority_value,
            "owner": FieldResolver.extract_field_value(item, get_field_key("owner")),
        }

    async def simplify_work_items(
        self,
        items: List[Dict[str, Any]],
        field_mapping: Optional[Dict[str, str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        批量简化工作项列表

        Args:
            items: 原始工作项列表
            field_mapping: 字段名称到字段Key的映射（可选）

        Returns:
            简化后的工作项列表，owner 字段会转换为人名以提高可读性
        """
        logger.info("simplify_work_items: processing %d items", len(items))
        if items:
            logger.info("First item keys: %s", list(items[0].keys()))
            if "fields" in items[0]:
                fields = items[0].get("fields", [])
                logger.info(
                    "First item fields count: %d, field_keys: %s",
                    len(fields),
                    [f.get("field_key") for f in fields],
                )

        # 并行简化所有工作项
        tasks = [self.simplify_work_item(item, field_mapping) for item in items]
        simplified_items = await asyncio.gather(*tasks)

        # 批量转换 owner user_key 为人名
        owner_keys = [
            item["owner"]
            for item in simplified_items
            if (owner := item.get("owner"))
            and isinstance(owner, str)
            and owner.isdigit()
            and len(owner) > 10
        ]

        if owner_keys:
            unique_keys = list(set(owner_keys))
            logger.info("Converting %d unique owner keys to names", len(unique_keys))
            try:
                key_to_name = await self.meta.batch_get_user_names(unique_keys)
                # 替换 owner 字段
                for item in simplified_items:
                    owner = item.get("owner")
                    if owner and owner in key_to_name:
                        item["owner"] = key_to_name[owner]
            except Exception as e:
                logger.warning("Failed to convert owner keys to names: %s", e)

        return list(simplified_items)

    async def enhance_with_readable_names(
        self,
        item: Dict[str, Any],
        project_key: str,
        type_key: str,
        api: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        增强工作项数据，将字段 Key 和 ID 转换为可读名称

        Args:
            item: 原始工作项字典
            project_key: 项目 Key
            type_key: 工作项类型 Key
            api: WorkItemAPI 实例（用于获取关联工作项名称）

        Returns:
            增强后的工作项字典，包含 readable_fields 字段
        """
        if not item:
            return item

        # 创建副本，避免修改原始数据
        enhanced = item.copy()

        # 准备收集 ID 的容器
        users_to_fetch: Set[str] = set()
        work_items_to_fetch: Set[int] = set()

        # 统一处理 fields (新版) 和 field_value_pairs (旧版)
        fields = list(item.get("fields", []))
        if not fields:
            field_value_pairs = item.get("field_value_pairs", [])
            for pair in field_value_pairs:
                fields.append(
                    {
                        "field_key": pair.get("field_key"),
                        "field_value": pair.get("field_value"),
                        "field_type_key": "unknown",
                    }
                )

        # 第一遍遍历: 收集需要查询的 ID
        for field in fields:
            f_val = field.get("field_value")
            f_type = field.get("field_type_key", "")

            if not f_val:
                continue

            # 用户相关字段
            if f_type in ["user", "owner", "creator", "modifier"]:
                if isinstance(f_val, list):
                    for u in f_val:
                        if isinstance(u, dict) and "user_key" in u:
                            users_to_fetch.add(u["user_key"])
                        elif isinstance(u, str):
                            users_to_fetch.add(u)
                elif isinstance(f_val, dict) and "user_key" in f_val:
                    users_to_fetch.add(f_val["user_key"])
                elif isinstance(f_val, str):
                    users_to_fetch.add(f_val)

            # 工作项关联字段
            elif f_type in ["work_item", "work_item_related"]:
                if isinstance(f_val, list):
                    for wid in f_val:
                        if isinstance(wid, int):
                            work_items_to_fetch.add(wid)
                        elif isinstance(wid, str) and wid.isdigit():
                            work_items_to_fetch.add(int(wid))
                elif isinstance(f_val, int):
                    work_items_to_fetch.add(f_val)
                elif isinstance(f_val, str) and f_val.isdigit():
                    work_items_to_fetch.add(int(f_val))

        # 批量获取用户名称
        user_map: Dict[str, str] = {}
        if users_to_fetch:
            try:
                user_map = await self.meta.batch_get_user_names(list(users_to_fetch))
            except Exception as e:
                logger.warning("Failed to fetch user names: %s", e)

        # 批量获取工作项名称
        work_item_map: Dict[int, str] = {}
        if work_items_to_fetch and api is not None:
            try:
                work_item_map, _ = await self._get_work_items_with_cache(
                    list(work_items_to_fetch), project_key, type_key, api
                )
            except Exception as e:
                logger.warning("Failed to fetch work item names: %s", e)

        # 第二遍遍历: 构建可读字段
        readable_fields: Dict[str, Any] = {}

        for field in fields:
            f_key = field.get("field_key")
            f_val = field.get("field_value")
            f_type = field.get("field_type_key", "")

            # 获取字段名称
            try:
                field_name = await self.meta.get_field_name(
                    project_key, type_key, f_key
                )
            except Exception:
                field_name = field.get("field_alias") or f_key

            field["field_name"] = field_name

            readable_val = FieldResolver.extract_readable_field_value(f_val)

            # 用户字段增强
            if f_type in ["user", "owner", "creator", "modifier"]:
                if isinstance(f_val, list):
                    readable_val = [
                        user_map.get(
                            u.get("user_key", u) if isinstance(u, dict) else u,
                            u.get("name_cn", u.get("name", u))
                            if isinstance(u, dict)
                            else u,
                        )
                        for u in f_val
                    ]
                elif isinstance(f_val, dict):
                    uk = f_val.get("user_key")
                    readable_val = user_map.get(
                        uk, f_val.get("name_cn", f_val.get("name", uk))
                    )
                elif isinstance(f_val, str):
                    readable_val = user_map.get(f_val, f_val)

            # 工作项关联字段增强
            elif f_type in ["work_item", "work_item_related"]:
                if isinstance(f_val, list):
                    readable_val = [
                        work_item_map.get(
                            int(wid) if isinstance(wid, str) else wid, wid
                        )
                        for wid in f_val
                    ]
                elif isinstance(f_val, (int, str)) and str(f_val).isdigit():
                    readable_val = work_item_map.get(int(f_val), f_val)

            # 选项字段增强
            elif isinstance(f_val, dict) and ("label" in f_val or "name" in f_val):
                readable_val = f_val.get("label") or f_val.get("name")
            elif isinstance(f_val, list) and f_val and isinstance(f_val[0], dict):
                if f_type not in ["user", "owner", "creator", "modifier"]:
                    readable_val = [
                        item.get("label") or item.get("name") or item
                        for item in f_val
                        if isinstance(item, dict)
                    ]

            readable_fields[field_name] = readable_val

        enhanced["fields"] = fields
        enhanced["readable_fields"] = readable_fields

        # 处理根目录特殊字段
        for key in ["owner", "created_by", "updated_by"]:
            val = item.get(key)
            if val and isinstance(val, str):
                readable_fields[key] = user_map.get(val, val)

        # 为常用字段添加顶级可读别名
        for field in ["owner", "creator", "updater", "assignee"]:
            if field in readable_fields:
                enhanced[f"readable_{field}"] = readable_fields[field]

        return enhanced

    async def _get_work_items_with_cache(
        self,
        work_item_ids: List[int],
        project_key: str,
        type_key: str,
        api: Any,
    ) -> tuple[Dict[int, str], List[int]]:
        """
        通过缓存获取工作项名称

        Args:
            work_item_ids: 工作项 ID 列表
            project_key: 项目 Key
            type_key: 工作项类型 Key
            api: WorkItemAPI 实例

        Returns:
            (工作项 ID 到名称的映射字典, 未找到的 ID 列表)
        """
        work_item_map: Dict[int, str] = {}
        items_to_fetch: List[int] = []

        # 首先检查缓存
        if self._work_item_cache:
            for item_id in work_item_ids:
                cached_value = self._work_item_cache.get(str(item_id))
                if cached_value is not None:
                    if cached_value != self._NOT_FOUND_MARKER:
                        work_item_map[item_id] = cached_value
                else:
                    items_to_fetch.append(item_id)
        else:
            items_to_fetch = list(work_item_ids)

        # 如果有未缓存的工作项，批量查询
        not_found_ids: List[int] = []
        if items_to_fetch:
            try:
                items = await api.query(project_key, type_key, items_to_fetch)
                found_ids: Set[int] = set()
                for item in items:
                    item_id = item.get("id")
                    item_name = item.get("name") or ""
                    if item_id:
                        work_item_map[item_id] = item_name
                        if self._work_item_cache:
                            self._work_item_cache.set(str(item_id), item_name)
                        found_ids.add(item_id)

                not_found_ids = [
                    item_id for item_id in items_to_fetch if item_id not in found_ids
                ]
                if self._work_item_cache:
                    for item_id in not_found_ids:
                        self._work_item_cache.set(str(item_id), self._NOT_FOUND_MARKER)

            except Exception as e:
                logger.debug("Failed to fetch work items in current type: %s", e)
                not_found_ids = items_to_fetch

        return work_item_map, not_found_ids
