import pytest
from unittest.mock import AsyncMock, patch
from src.services.issue_service import IssueService

@pytest.fixture
def mock_provider():
    with patch("src.services.issue_service.WorkItemProvider") as mock:
        yield mock.return_value

@pytest.mark.asyncio
async def test_create_issue(mock_provider):
    mock_provider.create_issue = AsyncMock(return_value=123)
    
    service = IssueService(project_name="Test Project")
    res = await service.create_issue("Title", "P1")
    
    assert "123" in res
    mock_provider.create_issue.assert_awaited_with(
        name="Title", priority="P1", description="", assignee=None
    )

@pytest.mark.asyncio
async def test_get_issue(mock_provider):
    mock_provider.get_issue_details = AsyncMock(return_value={"id": 1})
    
    service = IssueService(project_name="Test Project")
    res = await service.get_issue(1)
    
    assert res["id"] == 1
    mock_provider.get_issue_details.assert_awaited_with(1)
