"""
RoleAPI - 角色管理原子能力层
负责角色查询、成员获取等原子接口封装

对应 Postman 集合:
- 流程配置 > 获取角色列表: GET /open_api/:project_key/role/all
- 流程配置 > 查询角色成员: POST /open_api/:project_key/role/member/query
"""

import logging
from typing import Dict, List, Optional
from src.core.project_client import get_project_client, ProjectClient

logger = logging.getLogger(__name__)


class RoleAPI:
    """
    飞书项目角色 API 封装 (Base API Layer)
    """

    def __init__(self, client: Optional[ProjectClient] = None):
        self.client = client or get_project_client()

    async def get_roles(self, project_key: str) -> List[Dict]:
        """
        获取角色列表

        对应 Postman: 流程配置 > 获取角色列表
        API: GET /open_api/:project_key/role/all

        Args:
            project_key: 项目空间 Key

        Returns:
            角色列表，每项包含 {role_key, name, ...}

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"/open_api/{project_key}/role/all"

        logger.debug("Getting roles: project_key=%s", project_key)

        resp = await self.client.get(url)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "获取角色列表失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"获取角色列表失败: {err_msg}")

        roles = data.get("data", [])
        logger.info("Retrieved %d roles", len(roles))
        return roles

    async def query_role_members(
        self,
        project_key: str,
        role_key: str,
        page_num: int = 1,
        page_size: int = 50,
    ) -> Dict:
        """
        查询角色成员

        对应 Postman: 流程配置 > 查询角色成员
        API: POST /open_api/:project_key/role/member/query

        Args:
            project_key: 项目空间 Key
            role_key: 角色 Key
            page_num: 页码
            page_size: 每页数量

        Returns:
            角色成员列表及分页信息

        Raises:
            Exception: API 调用失败时抛出异常
        """
        url = f"/open_api/{project_key}/role/member/query"
        payload = {
            "role_key": role_key,
            "page_num": page_num,
            "page_size": page_size,
        }

        logger.debug(
            "Querying role members: project=%s, role=%s",
            project_key,
            role_key,
        )

        resp = await self.client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

        if data.get("err_code") != 0:
            err_msg = data.get("err_msg", "Unknown error")
            logger.error(
                "查询角色成员失败: err_code=%s, err_msg=%s",
                data.get("err_code"),
                err_msg,
            )
            raise Exception(f"查询角色成员失败: {err_msg}")

        result = data.get("data", {})
        count = len(result.get("members", []))
        logger.info("Retrieved %d role members", count)
        return result
