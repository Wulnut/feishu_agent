"""
ProjectAPI - L1 原子能力层
负责空间/项目维度的原子接口封装

对应 Postman 集合:
- 空间 > 获取空间列表: POST /open_api/projects
- 空间 > 获取空间详情: POST /open_api/projects/detail
"""

from typing import Dict, List, Optional, Any
from src.core.project_client import get_project_client, ProjectClient
from src.core.config import settings


class ProjectAPI:
    """
    飞书项目空间 API 封装 (L1 - Base API Layer)

    职责: 严格对应 Postman 集合中的空间相关原子接口
    """

    def __init__(self, client: Optional[ProjectClient] = None):
        self.client = client or get_project_client()

    async def list_projects(
        self,
        user_key: Optional[str] = None,
        tenant_group_id: int = 0,
        asset_key: Optional[str] = None,
        order: Optional[List[str]] = None,
    ) -> List[str]:
        """
        获取空间列表

        对应 Postman: 空间 > 获取空间列表
        API: POST /open_api/projects

        Args:
            user_key: 用户 Key，不传则使用配置中的默认值
            tenant_group_id: 租户组 ID，默认 0
            asset_key: 资产 Key
            order: 排序字段列表

        Returns:
            项目 Key 列表 (List[str])

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = "/open_api/projects"
        payload: Dict[str, Any] = {
            "user_key": user_key or settings.FEISHU_PROJECT_USER_KEY,
            "tenant_group_id": tenant_group_id,
        }

        if asset_key:
            payload["asset_key"] = asset_key
        if order:
            payload["order"] = order

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            raise Exception(f"获取空间列表失败: {data.get('err_msg')}")

        return data.get("data", [])

    async def get_project_details(
        self,
        project_keys: List[str],
        user_key: Optional[str] = None,
        simple_names: Optional[List[str]] = None,
        tenant_group_id: int = 0,
    ) -> Dict[str, Dict]:
        """
        获取空间详情

        对应 Postman: 空间 > 获取空间详情
        API: POST /open_api/projects/detail

        Args:
            project_keys: 项目 Key 列表
            user_key: 用户 Key
            simple_names: 简称列表 (可用于按名称查询)
            tenant_group_id: 租户组 ID

        Returns:
            项目详情字典 {project_key: {name, simple_name, ...}}

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = "/open_api/projects/detail"
        payload: Dict[str, Any] = {
            "project_keys": project_keys,
            "user_key": user_key or settings.FEISHU_PROJECT_USER_KEY,
            "tenant_group_id": tenant_group_id,
        }

        if simple_names:
            payload["simple_names"] = simple_names

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            raise Exception(f"获取空间详情失败: {data.get('err_msg')}")

        return data.get("data", {})
