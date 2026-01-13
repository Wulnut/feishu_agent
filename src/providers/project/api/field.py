"""
FieldAPI - L3 原子能力层
负责字段配置相关的原子接口封装

对应 Postman 集合:
- 配置 > 工作项配置 > 字段配置 > 获取字段信息: POST /open_api/:project_key/field/all
- 配置 > 工作项配置 > 字段配置 > 创建自定义字段: POST /open_api/:project_key/field/:work_item_type_key/create
- 配置 > 工作项配置 > 字段配置 > 更新自定义字段: PUT /open_api/:project_key/field/:work_item_type_key
"""

from typing import Dict, List, Optional, Any
from src.core.project_client import get_project_client, ProjectClient


class FieldAPI:
    """
    飞书项目字段 API 封装 (L3 - Base API Layer)

    职责: 严格对应 Postman 集合中的字段配置相关原子接口
    依赖: L2 (需要 project_key 和 work_item_type_key)
    """

    def __init__(self, client: Optional[ProjectClient] = None):
        self.client = client or get_project_client()

    async def get_all_fields(
        self, project_key: str, work_item_type_key: str
    ) -> List[Dict]:
        """
        获取字段信息

        对应 Postman: 配置 > 工作项配置 > 字段配置 > 获取字段信息
        API: POST /open_api/:project_key/field/all

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key

        Returns:
            字段列表，每项包含 {field_name, field_key, field_alias, options, ...}

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"/open_api/{project_key}/field/all"
        payload = {"work_item_type_key": work_item_type_key}

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            raise Exception(f"获取字段信息失败: {data.get('err_msg')}")

        return data.get("data", [])

    async def create_field(
        self,
        project_key: str,
        work_item_type_key: str,
        field_name: str,
        field_type_key: str,
        **kwargs,
    ) -> Dict:
        """
        创建自定义字段

        对应 Postman: 配置 > 工作项配置 > 字段配置 > 创建自定义字段
        API: POST /open_api/:project_key/field/:work_item_type_key/create

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key
            field_name: 字段名称
            field_type_key: 字段类型 Key
            **kwargs: 其他可选参数 (field_alias, help_description, default_value, ...)

        Returns:
            创建结果，包含 field_key

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"/open_api/{project_key}/field/{work_item_type_key}/create"
        payload: Dict[str, Any] = {
            "field_name": field_name,
            "field_type_key": field_type_key,
            **kwargs,
        }

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            raise Exception(f"创建自定义字段失败: {data.get('err_msg')}")

        return data.get("data", {})

    async def update_field(
        self, project_key: str, work_item_type_key: str, field_key: str, **kwargs
    ) -> Dict:
        """
        更新自定义字段

        对应 Postman: 配置 > 工作项配置 > 字段配置 > 更新自定义字段
        API: PUT /open_api/:project_key/field/:work_item_type_key

        Args:
            project_key: 项目空间 Key
            work_item_type_key: 工作项类型 Key
            field_key: 字段 Key
            **kwargs: 更新的字段属性 (field_name, field_alias, help_description, ...)

        Returns:
            更新结果

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"/open_api/{project_key}/field/{work_item_type_key}"
        payload: Dict[str, Any] = {"field_key": field_key, **kwargs}

        resp = await self.client.put(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            raise Exception(f"更新自定义字段失败: {data.get('err_msg')}")

        return data.get("data", {})

    async def get_work_item_relations(self, project_key: str) -> List[Dict]:
        """
        获取工作项关系列表

        对应 Postman: 配置 > 工作项配置 > 工作项关系配置 > 获取工作项关系列表
        API: GET /open_api/:project_key/work_item/relation

        Args:
            project_key: 项目空间 Key

        Returns:
            工作项关系列表

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"/open_api/{project_key}/work_item/relation"

        resp = await self.client.get(url)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            raise Exception(f"获取工作项关系列表失败: {data.get('err_msg')}")

        return data.get("data", [])
