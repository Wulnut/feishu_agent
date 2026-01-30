import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.providers.lark_project.api.metadata import MetadataAPI
from src.providers.lark_project.api.field import FieldAPI
from src.providers.lark_project.api.work_item import WorkItemAPI


@pytest.fixture
def mock_client():
    client = AsyncMock()
    # Create a MagicMock for the response, since json() and raise_for_status() are sync
    mock_response = MagicMock()
    mock_response.json.return_value = {"err_code": 0, "data": {}}
    mock_response.raise_for_status.return_value = None

    # Configure client methods to return this mock_response
    client.get.return_value = mock_response
    client.post.return_value = mock_response
    client.put.return_value = mock_response
    return client


@pytest.mark.asyncio
async def test_update_work_item_type_config(mock_client):
    api = MetadataAPI(client=mock_client)
    mock_client.put.return_value.json.return_value = {
        "err_code": 0,
        "data": {"key": "value"},
    }

    result = await api.update_work_item_type_config(
        "proj_key", "type_key", {"desc": "new"}
    )

    assert result == {"key": "value"}
    mock_client.put.assert_called_once_with(
        "/open_api/proj_key/work_item/type/type_key", json={"desc": "new"}
    )


@pytest.mark.asyncio
async def test_get_workflows(mock_client):
    api = MetadataAPI(client=mock_client)
    mock_client.get.return_value.json.return_value = {
        "err_code": 0,
        "data": [{"uuid": "1"}],
    }

    result = await api.get_workflows("proj_key", "type_key")

    assert result == [{"uuid": "1"}]
    mock_client.get.assert_called_once_with("/open_api/proj_key/workflow/type_key")


@pytest.mark.asyncio
async def test_create_work_item_relation(mock_client):
    api = FieldAPI(client=mock_client)
    mock_client.post.return_value.json.return_value = {
        "err_code": 0,
        "data": {"id": 123},
    }

    result = await api.create_work_item_relation("proj", "rel_name", "start", "end")

    assert result == {"id": 123}
    mock_client.post.assert_called_once()
    args, kwargs = mock_client.post.call_args
    assert args[0] == "/open_api/work_item/relation/create"
    assert kwargs["json"]["project_key"] == "proj"


@pytest.mark.asyncio
async def test_update_work_item_relation(mock_client):
    api = FieldAPI(client=mock_client)
    mock_client.post.return_value.json.return_value = {
        "err_code": 0,
        "data": {"updated": True},
    }

    result = await api.update_work_item_relation("rel_key", name="new_name")

    assert result == {"updated": True}
    mock_client.post.assert_called_once()
    args, kwargs = mock_client.post.call_args
    assert args[0] == "/open_api/work_item/relation/update"
    assert kwargs["json"]["relation_key"] == "rel_key"
    assert kwargs["json"]["name"] == "new_name"


@pytest.mark.asyncio
async def test_search_by_relation(mock_client):
    api = WorkItemAPI()
    with patch.object(api, "client", mock_client):
        mock_client.post.return_value.json.return_value = {
            "err_code": 0,
            "data": {"work_items": []},
        }

        result = await api.search_by_relation("proj_1", "type_1", 123)

        assert result == {"work_items": []}
        mock_client.post.assert_called_once()
        args, kwargs = mock_client.post.call_args
        assert args[0] == "/open_api/proj_1/work_item/type_1/123/search_by_relation"
