import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.providers.lark_project.api.work_item import WorkItemAPI
from src.providers.lark_project.api.attachment import AttachmentAPI
from src.providers.lark_project.api.role import RoleAPI
from src.providers.lark_project.api.metadata import MetadataAPI


@pytest.fixture
def mock_client():
    client = AsyncMock()
    mock_response = MagicMock()
    mock_response.json.return_value = {"err_code": 0, "data": {}}
    mock_response.raise_for_status.return_value = None
    client.get.return_value = mock_response
    client.post.return_value = mock_response
    client.put.return_value = mock_response
    return client


# Tier 1 Tests


@pytest.mark.asyncio
async def test_get_operate_history(mock_client):
    api = WorkItemAPI()
    with patch.object(api, "client", mock_client):
        mock_client.get.return_value.json.return_value = {
            "err_code": 0,
            "data": [{"id": 1}],
        }

        result = await api.get_operate_history("proj", "type", 123)

        assert len(result) == 1
        mock_client.get.assert_called_once()
        args, kwargs = mock_client.get.call_args
        assert "operate-history" in args[0]
        assert kwargs["params"]["page_num"] == 1


@pytest.mark.asyncio
async def test_delete_file(mock_client):
    api = AttachmentAPI(client=mock_client)
    mock_client.post.return_value.json.return_value = {
        "err_code": 0,
        "data": {"success": True},
    }

    result = await api.delete_file("proj", ["token1"])

    assert result == {"success": True}
    mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_roles(mock_client):
    api = RoleAPI(client=mock_client)
    mock_client.get.return_value.json.return_value = {
        "err_code": 0,
        "data": [{"key": "role1"}],
    }

    result = await api.get_roles("proj")

    assert len(result) == 1
    mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_query_role_members(mock_client):
    api = RoleAPI(client=mock_client)
    mock_client.post.return_value.json.return_value = {
        "err_code": 0,
        "data": {"members": []},
    }

    result = await api.query_role_members("proj", "role1")

    assert "members" in result
    mock_client.post.assert_called_once()


# Tier 2 Tests


@pytest.mark.asyncio
async def test_query_man_hour(mock_client):
    api = WorkItemAPI()
    with patch.object(api, "client", mock_client):
        mock_client.post.return_value.json.return_value = {
            "err_code": 0,
            "data": [{"hours": 5}],
        }

        result = await api.query_man_hour("proj", "type", [1, 2])

        assert len(result) == 1
        mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_update_actual_time(mock_client):
    api = WorkItemAPI()
    with patch.object(api, "client", mock_client):
        mock_client.post.return_value.json.return_value = {
            "err_code": 0,
            "data": {"updated": True},
        }

        result = await api.update_actual_time("proj", "type", 123, 60)

        assert result == {"updated": True}
        mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_get_workflow_detail(mock_client):
    api = MetadataAPI(client=mock_client)
    mock_client.get.return_value.json.return_value = {
        "err_code": 0,
        "data": {"detail": "info"},
    }

    result = await api.get_workflow_detail("proj", "type", 999)

    assert result == {"detail": "info"}
    mock_client.get.assert_called_once()
