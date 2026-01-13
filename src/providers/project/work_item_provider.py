from typing import List, Dict, Optional, Any
from src.providers.base import Provider
from src.providers.project.api.work_item import WorkItemAPI
from src.providers.project.managers import MetadataManager
import logging

logger = logging.getLogger(__name__)


class WorkItemProvider(Provider):
    """
    工作项业务逻辑提供者 (Service/Provider Layer)
    串联 MetadataManager 和 WorkItemAPI，提供人性化的接口

    设计说明:
    - 使用 MetadataManager 实现零硬编码: 所有 Key/Value 通过名称动态解析
    - 使用 WorkItemAPI 执行原子操作
    """

    def __init__(
        self,
        project_name: Optional[str] = None,
        project_key: Optional[str] = None,
        work_item_type_name: str = "Issue管理",
    ):
        if not project_name and not project_key:
            raise ValueError("Must provide either project_name or project_key")

        self.project_name = project_name
        self._project_key = project_key
        self.work_item_type_name = work_item_type_name
        self.api = WorkItemAPI()
        self.meta = MetadataManager.get_instance()

    async def _get_project_key(self) -> str:
        if not self._project_key:
            if self.project_name:
                self._project_key = await self.meta.get_project_key(self.project_name)
            else:
                raise ValueError("Project key not resolved")
        return self._project_key

    async def _resolve_field_value(
        self, project_key: str, type_key: str, field_key: str, value: Any
    ) -> Any:
        """解析字段值：如果是 Select 类型且值为 Label，转换为 Option Value"""
        try:
            val = await self.meta.get_option_value(
                project_key, type_key, field_key, str(value)
            )
            logger.info(f"Resolved option '{value}' -> '{val}' for field '{field_key}'")
            return val
        except Exception as e:
            logger.warning(
                f"Failed to resolve option '{value}' for field '{field_key}': {e}"
            )
            return value  # Fallback

    async def create_issue(
        self,
        name: str,
        priority: str = "P2",
        description: str = "",
        assignee: Optional[str] = None,
    ) -> int:
        """
        创建 Issue
        """
        project_key = await self._get_project_key()
        type_key = await self.meta.get_type_key(project_key, self.work_item_type_name)

        logger.info(f"Creating Issue in Project: {project_key}, Type: {type_key}")

        # 1. Prepare fields for creation (minimal set)
        create_fields = []

        # Description
        if description:
            field_key = await self.meta.get_field_key(
                project_key, type_key, "description"
            )
            create_fields.append({"field_key": field_key, "field_value": description})

        # Assignee
        if assignee:
            field_key = "owner"
            user_key = await self.meta.get_user_key(assignee)
            create_fields.append({"field_key": field_key, "field_value": user_key})

        # 2. Create Work Item
        issue_id = await self.api.create(project_key, type_key, name, create_fields)

        # 3. Update Priority (if needed)
        # Note: Priority cannot be set during creation for some reason, so we update it after.
        if priority:
            try:
                field_key = await self.meta.get_field_key(
                    project_key, type_key, "priority"
                )
                option_val = await self._resolve_field_value(
                    project_key, type_key, field_key, priority
                )

                logger.info(f"Updating priority to {option_val}...")
                await self.api.update(
                    project_key,
                    type_key,
                    issue_id,
                    [{"field_key": field_key, "field_value": option_val}],
                )
            except Exception as e:
                logger.warning(f"Failed to update priority: {e}")

        return issue_id

    async def get_issue_details(self, issue_id: int) -> Dict:
        """获取 Issue 详情"""
        project_key = await self._get_project_key()
        type_key = await self.meta.get_type_key(project_key, self.work_item_type_name)

        items = await self.api.query(project_key, type_key, [issue_id])
        if not items:
            raise Exception(f"Issue {issue_id} not found")
        return items[0]

    async def delete_issue(self, issue_id: int) -> None:
        """删除 Issue"""
        project_key = await self._get_project_key()
        type_key = await self.meta.get_type_key(project_key, self.work_item_type_name)
        await self.api.delete(project_key, type_key, issue_id)
