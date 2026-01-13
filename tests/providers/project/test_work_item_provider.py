import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.providers.project.work_item_provider import WorkItemProvider


@pytest.fixture
def mock_api():
    with patch("src.providers.project.work_item_provider.WorkItemAPI") as mock:
        yield mock.return_value


@pytest.fixture
def mock_metadata():
    with patch("src.providers.project.work_item_provider.MetadataManager") as mock_cls:
        mock_instance = AsyncMock()
        mock_cls.get_instance.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_create_issue(mock_api, mock_metadata):
    # Setup mocks
    mock_metadata.get_project_key.return_value = "proj_123"
    mock_metadata.get_type_key.return_value = "type_issue"
    mock_metadata.get_field_key.side_effect = lambda pk, tk, name: f"field_{name}"
    mock_metadata.get_option_value.return_value = "opt_high"
    mock_metadata.get_user_key.return_value = "user_456"

    mock_api.create = AsyncMock(return_value=1001)
    mock_api.update = AsyncMock()

    # Init provider
    provider = WorkItemProvider("My Project")

    # Execute
    issue_id = await provider.create_issue(
        name="Test Issue", priority="High", description="Desc", assignee="Alice"
    )

    # Verify
    assert issue_id == 1001

    # Check Metadata calls
    mock_metadata.get_project_key.assert_awaited_with("My Project")
    mock_metadata.get_type_key.assert_awaited_with("proj_123", "Issue管理")

    # Check Create call
    # Create should be called with minimal fields first
    mock_api.create.assert_awaited_once()
    args, _ = mock_api.create.call_args
    assert args[0] == "proj_123"
    assert args[1] == "type_issue"
    assert args[2] == "Test Issue"

    fields = args[3]
    # Expect description and owner in create fields
    assert any(
        f["field_key"] == "field_description" and f["field_value"] == "Desc"
        for f in fields
    )
    assert any(
        f["field_key"] == "owner" and f["field_value"] == "user_456" for f in fields
    )

    # Check Update call (for priority)
    mock_api.update.assert_awaited_once()
    args, _ = mock_api.update.call_args
    assert args[2] == 1001  # issue_id
    update_fields = args[3]
    assert update_fields[0]["field_key"] == "field_priority"
    assert update_fields[0]["field_value"] == "opt_high"


@pytest.mark.asyncio
async def test_get_issue_details(mock_api, mock_metadata):
    mock_metadata.get_project_key.return_value = "proj_123"
    mock_metadata.get_type_key.return_value = "type_issue"

    mock_api.query = AsyncMock(return_value=[{"id": 1001, "name": "Issue"}])

    provider = WorkItemProvider("My Project")
    details = await provider.get_issue_details(1001)

    assert details["id"] == 1001
    mock_api.query.assert_awaited_with("proj_123", "type_issue", [1001])


@pytest.mark.asyncio
async def test_delete_issue(mock_api, mock_metadata):
    mock_metadata.get_project_key.return_value = "proj_123"
    mock_metadata.get_type_key.return_value = "type_issue"
    mock_api.delete = AsyncMock()

    provider = WorkItemProvider("My Project")
    await provider.delete_issue(1001)

    mock_api.delete.assert_awaited_with("proj_123", "type_issue", 1001)
