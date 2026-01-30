"""
字段解析器 - 负责字段值的解析、转换和提取

职责：
- 解析原始字段值为可读格式
- 从工作项中提取字段值
- 解析选项字段的 Label/Value 转换
- 解析负责人字段 Key

设计说明：
- 依赖 MetadataManager 获取字段元数据
- 所有解析方法都是无状态的，仅依赖传入的参数
"""

import logging
from typing import Any, Dict, Optional, Tuple

from src.providers.lark_project.managers import MetadataManager

logger = logging.getLogger(__name__)


# 负责人字段的候选名称列表（按优先级排序）
OWNER_FIELD_CANDIDATES: Tuple[str, ...] = (
    "owner",
    "当前负责人",
    "负责人",
    "经办人",
    "Assignee",
)


class FieldResolver:
    """
    字段解析器

    提供字段值解析、提取和转换的统一接口。

    Attributes:
        meta: MetadataManager 实例，用于获取字段元数据
    """

    def __init__(self, meta: MetadataManager):
        """
        初始化字段解析器

        Args:
            meta: MetadataManager 实例
        """
        self.meta = meta

    # ========== 静态解析方法 ==========

    @staticmethod
    def parse_raw_field_value(value: Any) -> Optional[str]:
        """
        解析原始字段值为可读字符串

        Args:
            value: 原始字段值，可以是 dict、list 或其他类型

        Returns:
            解析后的字符串值，如果无法解析则返回 None
        """
        if value is None:
            return None
        # 选项类型字段: {label: "...", value: "..."}
        if isinstance(value, dict):
            return value.get("label") or value.get("value")
        # 用户类型字段: [{name: "...", name_cn: "..."}]
        if isinstance(value, list) and value and isinstance(value[0], dict):
            return value[0].get("name") or value[0].get("name_cn")
        # 其他类型: 转为字符串
        return str(value) if value else None

    @staticmethod
    def extract_field_value(item: Dict[str, Any], field_key: str) -> Optional[str]:
        """
        从工作项中提取字段值

        支持两种数据结构：
        1. fields: 新版结构，字段以对象列表形式存在
        2. field_value_pairs: 旧版结构，字段以键值对列表形式存在

        Args:
            item: 工作项字典
            field_key: 字段 Key

        Returns:
            字段值（字符串），如果不存在则返回 None
        """
        # 优先从 fields 数组查找
        field = next(
            (f for f in item.get("fields", []) if f.get("field_key") == field_key),
            None,
        )
        if field:
            return FieldResolver.parse_raw_field_value(field.get("field_value"))

        # 回退到 field_value_pairs
        pair = next(
            (
                p
                for p in item.get("field_value_pairs", [])
                if p.get("field_key") == field_key
            ),
            None,
        )
        if pair:
            return FieldResolver.parse_raw_field_value(pair.get("field_value"))

        logger.debug(
            "Field key '%s' not found in item id=%s", field_key, item.get("id")
        )
        return None

    @staticmethod
    def extract_readable_field_value(field_value: Any) -> Any:
        """
        提取可读的字段值，特别处理用户相关字段

        Args:
            field_value: 原始字段值

        Returns:
            可读的字段值，如果无法提取则返回原始值
        """
        if field_value is None:
            return None

        # 如果是字典且包含 label 或 name 字段，优先返回这些
        if isinstance(field_value, dict):
            if "label" in field_value:
                return field_value["label"]
            if "name" in field_value:
                return field_value["name"]
            if "name_cn" in field_value:
                return field_value["name_cn"]
            # 如果字典中没有可读字段，返回整个字典（可能是复杂对象）
            return field_value

        # 如果是列表，处理每个元素
        if isinstance(field_value, list):
            # 空列表返回空列表
            if not field_value:
                return field_value

            # 单元素列表且元素是字典：尝试提取可读值
            if len(field_value) == 1 and isinstance(field_value[0], dict):
                single_item = field_value[0]
                # 尝试提取 name, name_cn, label
                for key in ["name", "name_cn", "label"]:
                    if key in single_item:
                        return single_item[key]
                # 如果没有可读键，返回整个字典
                return single_item

            # 多元素列表：处理每个元素
            readable_items = []
            for item in field_value:
                readable_item = FieldResolver.extract_readable_field_value(item)
                if readable_item is not None:
                    readable_items.append(readable_item)
            return readable_items if readable_items else field_value

        # 其他类型直接返回
        return field_value

    # ========== 异步解析方法（依赖 MetadataManager）==========

    async def resolve_field_value(
        self, project_key: str, type_key: str, field_key: str, value: Any
    ) -> Any:
        """
        解析字段值：如果是 Select 类型且值为 Label，转换为 Option Value（纯字符串）

        用于搜索/过滤 API，需要纯 value 字符串。

        Args:
            project_key: 项目空间 Key
            type_key: 工作项类型 Key
            field_key: 字段 Key
            value: 输入值（可以是 label 或 value）

        Returns:
            选项的 value 字符串，或原值（非选择类型）
        """
        try:
            option_value = await self.meta.get_option_value(
                project_key, type_key, field_key, str(value)
            )
            logger.info(
                "Resolved option '%s' -> '%s' for field '%s'",
                value,
                option_value,
                field_key,
            )
            return option_value
        except Exception as e:
            logger.warning(
                "Failed to resolve option '%s' for field '%s': %s",
                value,
                field_key,
                e,
            )
            return value  # Fallback: 非选择类型字段直接返回原值

    async def resolve_field_value_for_update(
        self, project_key: str, type_key: str, field_key: str, value: Any
    ) -> Any:
        """
        解析字段值用于更新 API：转换为 {label, value} 结构

        Args:
            project_key: 项目空间 Key
            type_key: 工作项类型 Key
            field_key: 字段 Key
            value: 输入值

        Returns:
            适用于更新 API 的字段值
        """
        # 特殊处理：针对 multi_select 字段，如果值为空，返回空列表 []
        try:
            field_type = await self.meta.get_field_type(
                project_key, type_key, field_key
            )
            if field_type == "multi_select" and (
                value is None or (isinstance(value, str) and not value.strip())
            ):
                logger.info(
                    "Empty value for multi_select field '%s', returning []", field_key
                )
                return []
        except Exception as e:
            logger.debug(
                "Failed to get field type in resolve_field_value_for_update: %s", e
            )

        # 处理列表 (多选)
        if isinstance(value, list):
            results = []
            for item in value:
                resolved_item = await self.resolve_field_value_for_update(
                    project_key, type_key, field_key, item
                )
                results.append(resolved_item)
            return results

        # 处理带分隔符的字符串 (伪多选支持)
        if isinstance(value, str) and any(
            sep in value for sep in (" / ", ",", ";", "|")
        ):
            # 先尝试不拆分直接匹配
            try:
                option_map = await self.meta.list_options(
                    project_key, type_key, field_key
                )
                if value in option_map:
                    return {"label": value, "value": option_map[value]}
            except Exception:
                pass

            # 尝试拆分
            for sep in (" / ", ",", ";", "|"):
                if sep in value:
                    parts = [p.strip() for p in value.split(sep) if p.strip()]
                    if len(parts) > 1:
                        logger.info(
                            "Detected multi-value with sep='%s': %s", sep, parts
                        )
                        results = []
                        for part in parts:
                            resolved = await self.resolve_field_value_for_update(
                                project_key, type_key, field_key, part
                            )
                            results.append(resolved)
                        return results
                    break

        # 处理单值（字符串、整数、布尔）
        try:
            # 获取选项映射
            option_map = await self.meta.list_options(project_key, type_key, field_key)
            str_value = str(value)

            # 尝试匹配 label
            if str_value in option_map:
                return {"label": str_value, "value": option_map[str_value]}

            # 尝试匹配 value（可能用户输入的是 value 本身）
            for label, opt_value in option_map.items():
                if opt_value == str_value:
                    return {"label": label, "value": opt_value}

            logger.debug(
                "Option not found for '%s' in field '%s', returning as-is",
                value,
                field_key,
            )
        except Exception as e:
            logger.debug(
                "Failed to get options for field '%s': %s, using value as-is",
                field_key,
                e,
            )

        # 处理布尔值
        try:
            field_type = await self.meta.get_field_type(
                project_key, type_key, field_key
            )
            if field_type == "bool" and isinstance(value, str):
                lower_val = value.lower()
                if lower_val in ("true", "yes", "on", "1"):
                    return True
                if lower_val in ("false", "no", "off", "0"):
                    return False
        except Exception:
            pass

        return value

    async def resolve_owner_field_key(self, project_key: str, type_key: str) -> str:
        """
        动态解析负责人字段 Key

        尝试按优先级顺序匹配候选字段名称。

        Args:
            project_key: 项目 Key
            type_key: 工作项类型 Key

        Returns:
            负责人字段 Key，默认为 "owner"
        """
        for candidate in OWNER_FIELD_CANDIDATES:
            try:
                key = await self.meta.get_field_key(project_key, type_key, candidate)
                if key:
                    logger.debug(
                        "Resolved owner field key to: %s ('%s')", key, candidate
                    )
                    return key
            except Exception:
                continue
        return "owner"  # 默认值
