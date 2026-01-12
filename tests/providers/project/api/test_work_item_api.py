import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.providers.project.api.work_item import WorkItemAPI

@pytest.fixture
def mock_client():
    with patch("src.providers.project.api.work_item.get_project_client") as mock:
        client_instance = AsyncMock()
        mock.return_value = client_instance
        yield client_instance

@pytest.fixture
def api(mock_client):
    return WorkItemAPI()

@pytest.mark.asyncio
async def test_create(api, mock_client):
    resp = MagicMock()
    resp.json.return_value = {"err_code": 0, "data": 12345}
    resp.raise_for_status = MagicMock()
    mock_client.post.return_value = resp
    
    res = await api.create("pk", "tk", "name", [{"field_key": "k", "field_value": "v"}])
    assert res == 12345
    
    mock_client.post.assert_awaited_once()
    args = mock_client.post.call_args
    assert args[0][0] == "/open_api/pk/work_item/create"
    assert args[1]["json"]["name"] == "name"

@pytest.mark.asyncio
async def test_query(api, mock_client):
    resp = MagicMock()
    resp.json.return_value = {"err_code": 0, "data": [{"id": 1}]}
    resp.raise_for_status = MagicMock()
    mock_client.post.return_value = resp
    
    res = await api.query("pk", "tk", [1])
    assert len(res) == 1
    assert res[0]["id"] == 1

@pytest.mark.asyncio
async def test_update(api, mock_client):
    resp = MagicMock()
    resp.json.return_value = {"err_code": 0, "data": {}}
    resp.raise_for_status = MagicMock()
    mock_client.put.return_value = resp
    
    await api.update("pk", "tk", 1, [])
    mock_client.put.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete(api, mock_client):
    resp = MagicMock()
    resp.json.return_value = {"err_code": 0, "data": {}}
    resp.raise_for_status = MagicMock()
    mock_client.delete.return_value = resp
    
    await api.delete("pk", "tk", 1)
    mock_client.delete.assert_awaited_once()

@pytest.mark.asyncio
async def test_filter(api, mock_client):
    resp = MagicMock()
    resp.json.return_value = {"err_code": 0, "data": {"items": []}}
    resp.raise_for_status = MagicMock()
    mock_client.post.return_value = resp
    
    await api.filter("pk", ["tk"])
    mock_client.post.assert_awaited_once()
    args = mock_client.post.call_args
    assert args[0][0] == "/open_api/pk/work_item/filter"

@pytest.mark.asyncio
async def test_search_params(api, mock_client):
    resp = MagicMock()
    resp.json.return_value = {"err_code": 0, "data": {}}
    resp.raise_for_status = MagicMock()
    mock_client.post.return_value = resp
    
    await api.search_params("pk", "tk", {"conjunction": "AND"})
    mock_client.post.assert_awaited_once()
    args = mock_client.post.call_args
    assert args[0][0] == "/open_api/pk/work_item/tk/search/params"
