"""
集成测试 - 工作项 E2E 流程测试 (Track 2)

测试环境:
- 项目: 主流程测试空间 (project_key: 66bb463229e5e58856b4ed19)
- 工作项类型: Issue管理

测试流程:
1. 创建工作项
2. 查询工作项
3. 更新工作项
4. 删除工作项（清理）

注意:
- 需要配置真实的飞书凭证 (FEISHU_PROJECT_USER_TOKEN, FEISHU_PROJECT_USER_KEY)
- 使用 pytest.mark.integration 标记
- 测试会自动保存 API 响应快照到 tests/fixtures/snapshots/
"""

import json
import pytest
from pathlib import Path

from tests.integration.conftest import (
    TEST_PROJECT_KEY,
    TEST_PROJECT_NAME,
    skip_without_credentials,
)


# =============================================================================
# Fixtures
# =============================================================================

SNAPSHOTS_DIR = Path(__file__).parent.parent / "fixtures" / "snapshots"


@pytest.fixture
def snapshot_saver():
    """保存 API 响应快照的 fixture"""
    def _save(filename: str, data: dict) -> None:
        SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = SNAPSHOTS_DIR / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n[Snapshot Saved] {filepath}")
    return _save


# =============================================================================
# E2E 测试
# =============================================================================


@pytest.mark.integration
@pytest.mark.asyncio
@skip_without_credentials
class TestWorkItemE2E:
    """工作项 CRUD E2E 测试"""

    async def test_full_crud_lifecycle(self, snapshot_saver):
        """
        完整的 CRUD 生命周期测试:
        Create -> Get -> Update -> Delete
        """
        from src.providers.project.work_item_provider import WorkItemProvider

        provider = WorkItemProvider(project_key=TEST_PROJECT_KEY)
        created_issue_id = None

        try:
            # =================================================================
            # Step 1: Create
            # =================================================================
            print("\n[Step 1] Creating issue...")
            created_issue_id = await provider.create_issue(
                name="[E2E Test] 自动化测试工作项",
                priority="P2",
                description="这是一个由集成测试自动创建的工作项，测试完成后会自动删除。",
            )
            assert created_issue_id is not None
            assert isinstance(created_issue_id, int)
            print(f"  -> Created issue_id: {created_issue_id}")

            # =================================================================
            # Step 2: Get (Query)
            # =================================================================
            print("\n[Step 2] Querying issue...")
            details = await provider.get_issue_details(created_issue_id)
            assert details is not None
            assert details["id"] == created_issue_id
            assert "[E2E Test]" in details.get("name", "")
            print(f"  -> Issue name: {details.get('name')}")

            # 保存快照 (供 Track 1 单元测试使用)
            snapshot_saver("work_item_detail.json", details)

            # =================================================================
            # Step 3: Update
            # =================================================================
            print("\n[Step 3] Updating issue...")
            await provider.update_issue(
                issue_id=created_issue_id,
                name="[E2E Test] 已更新的工作项",
                priority="P1",
            )
            print("  -> Update completed")

            # 验证更新
            updated_details = await provider.get_issue_details(created_issue_id)
            assert "[E2E Test] 已更新" in updated_details.get("name", "")
            print(f"  -> Updated name: {updated_details.get('name')}")

            # =================================================================
            # Step 4: List/Filter (获取列表用于快照)
            # =================================================================
            print("\n[Step 4] Listing issues...")
            list_result = await provider.get_tasks(page_size=10)
            assert "items" in list_result
            assert "total" in list_result
            print(f"  -> Total items: {list_result['total']}")

            # 保存列表快照
            snapshot_saver("work_item_list.json", list_result)

        finally:
            # =================================================================
            # Cleanup: Delete
            # =================================================================
            if created_issue_id:
                print(f"\n[Cleanup] Deleting issue {created_issue_id}...")
                try:
                    await provider.delete_issue(created_issue_id)
                    print("  -> Deleted successfully")
                except Exception as e:
                    print(f"  -> Warning: Failed to delete: {e}")

    async def test_filter_by_status(self, snapshot_saver):
        """测试按状态过滤"""
        from src.providers.project.work_item_provider import WorkItemProvider

        provider = WorkItemProvider(project_key=TEST_PROJECT_KEY)

        print("\n[Filter Test] Filtering by status...")
        result = await provider.filter_issues(
            status=["待处理"],
            page_size=5,
        )

        assert "items" in result
        assert "total" in result
        print(f"  -> Found {result['total']} items with status '待处理'")

        # 保存过滤结果快照
        if result["items"]:
            snapshot_saver("work_item_filter_by_status.json", result)

    async def test_list_available_options(self, snapshot_saver):
        """测试获取字段选项"""
        from src.providers.project.work_item_provider import WorkItemProvider

        provider = WorkItemProvider(project_key=TEST_PROJECT_KEY)

        print("\n[Options Test] Getting status options...")
        options = await provider.list_available_options("status")

        assert isinstance(options, dict)
        assert len(options) > 0
        print(f"  -> Available status options: {list(options.keys())}")

        # 保存选项快照
        snapshot_saver("field_options_status.json", {"field": "status", "options": options})

        print("\n[Options Test] Getting priority options...")
        priority_options = await provider.list_available_options("priority")
        print(f"  -> Available priority options: {list(priority_options.keys())}")

        snapshot_saver("field_options_priority.json", {"field": "priority", "options": priority_options})
