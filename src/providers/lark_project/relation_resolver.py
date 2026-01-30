"""
关联关系解析器 - 负责工作项关联关系的解析和查询

职责：
- 解析 related_to 参数（ID 或名称）
- 检查工作项是否关联指定 ID
- 在多个工作项类型中并行搜索关联项

设计说明：
- 依赖 MetadataManager 获取类型元数据
- 依赖 WorkItemAPI 执行关联查询
- 支持并行搜索提高效率
"""

import asyncio
import logging
from typing import Any, Dict, List, Tuple, Union

logger = logging.getLogger(__name__)


class RelationResolver:
    """
    关联关系解析器

    提供工作项关联关系解析和查询的统一接口。

    Attributes:
        api: WorkItemAPI 实例
        meta: MetadataManager 实例
    """

    # 搜索工作项的默认类型列表
    DEFAULT_SEARCH_TYPES: Tuple[str, ...] = (
        "项目管理",
        "需求管理",
        "Issue管理",
        "任务",
        "Epic",
        "事务管理",
    )

    def __init__(self, api: Any, meta: Any):
        """
        初始化关联关系解析器

        Args:
            api: WorkItemAPI 实例
            meta: MetadataManager 实例
        """
        self.api = api
        self.meta = meta

    @staticmethod
    def is_item_related_to(item: Dict[str, Any], related_to: int) -> bool:
        """
        检查工作项是否与指定 ID 关联

        Args:
            item: 工作项字典
            related_to: 关联的工作项 ID

        Returns:
            True: 关联，False: 不关联
        """
        for field in item.get("fields", []):
            field_value = field.get("field_value")
            if not field_value:
                continue
            if isinstance(field_value, list):
                if related_to in field_value:
                    return True
            elif field_value == related_to:
                return True
        return False

    async def resolve_related_to(
        self,
        related_to: Union[int, str],
        project_key: str,
        provider_factory: Any = None,
    ) -> int:
        """
        解析 related_to 参数，将名称转换为工作项 ID

        支持三种输入方式：
        1. 整数: 直接返回
        2. 数字字符串: 转换为整数返回
        3. 非数字字符串: 在多个工作项类型中并行搜索，返回匹配的 ID

        Args:
            related_to: 工作项 ID 或名称
            project_key: 项目 Key
            provider_factory: Provider 工厂函数（可选），用于创建子 Provider 搜索

        Returns:
            工作项 ID

        Raises:
            ValueError: 未找到匹配的工作项
        """
        # 整数: 直接返回
        if isinstance(related_to, int):
            logger.info("resolve_related_to: 直接使用整数 ID: %s", related_to)
            return related_to

        # 字符串处理
        if isinstance(related_to, str):
            # 数字字符串: 转换为整数
            if related_to.isdigit():
                result = int(related_to)
                logger.info("resolve_related_to: 字符串转整数 ID: %s", result)
                return result

            # 非数字字符串: 按名称并行搜索
            logger.info("resolve_related_to: 按名称并行搜索 '%s'", related_to)

            if provider_factory is None:
                raise ValueError(
                    f"无法按名称搜索 '{related_to}': 未提供 provider_factory"
                )

            async def search_single_type(
                search_type: str,
            ) -> Tuple[str, List[Dict[str, Any]]]:
                """搜索单个工作项类型，返回 (类型名, 结果列表)"""
                try:
                    temp_provider = provider_factory(
                        project_key=project_key,
                        work_item_type_name=search_type,
                    )
                    result = await temp_provider.api.filter(
                        project_key=project_key,
                        work_item_type_keys=[await temp_provider._get_type_key()],
                        work_item_name=related_to,
                        page_num=1,
                        page_size=10,
                    )
                    items = (
                        result.get("work_items", [])
                        if isinstance(result, dict)
                        else result
                        if isinstance(result, list)
                        else []
                    )
                    return (search_type, items)
                except Exception as e:
                    logger.debug("搜索类型 '%s' 失败: %s", search_type, e)
                    return (search_type, [])

            # 并行搜索所有类型
            results = await asyncio.gather(
                *(search_single_type(t) for t in self.DEFAULT_SEARCH_TYPES)
            )

            # 处理结果：优先精确匹配，其次部分匹配
            candidates: List[Tuple[Dict[str, Any], str]] = []

            for search_type, items in results:
                for item in items:
                    item_name = item.get("name")
                    if item_name == related_to:
                        # 发现精确匹配，直接返回
                        logger.info(
                            "resolve_related_to: 精确匹配 '%s' (ID: %s, Type: %s)",
                            item_name,
                            item.get("id"),
                            search_type,
                        )
                        return item.get("id")

                    # 收集部分匹配作为候选
                    candidates.append((item, search_type))

            # 如果没有精确匹配，检查候选者
            if candidates:
                best_match, match_type = candidates[0]
                logger.info(
                    "resolve_related_to: 部分匹配 '%s' (ID: %s, Type: %s)",
                    best_match.get("name"),
                    best_match.get("id"),
                    match_type,
                )
                return best_match.get("id")

            raise ValueError(f"未找到名称为 '{related_to}' 的工作项")

        # 其他类型: 尝试转换
        try:
            result = int(related_to)
            logger.info("resolve_related_to: 类型转换 ID: %s", result)
            return result
        except (ValueError, TypeError):
            raise ValueError(
                f"related_to 必须是工作项 ID（整数）或名称（字符串），当前类型: {type(related_to)}"
            )

    async def filter_related_items(
        self,
        items: List[Dict[str, Any]],
        related_to: int,
    ) -> List[Dict[str, Any]]:
        """
        过滤出与指定 ID 关联的工作项

        Args:
            items: 工作项列表
            related_to: 关联的工作项 ID

        Returns:
            过滤后的工作项列表
        """
        return [item for item in items if self.is_item_related_to(item, related_to)]
