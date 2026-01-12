import pytest
from unittest.mock import AsyncMock, MagicMock
from src.providers.project.metadata import MetadataService

@pytest.fixture
def mock_client():
    return AsyncMock()

@pytest.fixture
def service(mock_client):
    # Reset singleton
    MetadataService._instance = None
    return MetadataService(client=mock_client)

@pytest.mark.asyncio
async def test_get_project_key(service, mock_client):
    # Mock /projects response
    # Helper to create a sync response mock
    def create_response(data):
        resp = MagicMock()
        resp.json.return_value = data
        resp.raise_for_status = MagicMock()
        return resp

    mock_client.post.side_effect = [
        # List
        create_response({"err_code": 0, "data": ["key_1"]}),
        # Detail
        create_response({"err_code": 0, "data": {"key_1": {"name": "My Project"}}})
    ]
    
    # First call - API hit
    key = await service.get_project_key("My Project")
    assert key == "key_1"
    assert mock_client.post.call_count == 2
    
    # Second call - Cache hit
    mock_client.post.reset_mock()
    key2 = await service.get_project_key("My Project")
    assert key2 == "key_1"
    mock_client.post.assert_not_called()

@pytest.mark.asyncio
async def test_get_type_key(service, mock_client):
    # Mock /all-types
    resp = MagicMock()
    resp.json.return_value = {
        "err_code": 0, 
        "data": [{"name": "Bug", "type_key": "type_bug"}]
    }
    resp.raise_for_status = MagicMock()
    mock_client.get.return_value = resp
    
    key = await service.get_type_key("proj_1", "Bug")
    assert key == "type_bug"
    
    # Cache hit
    mock_client.get.reset_mock()
    await service.get_type_key("proj_1", "Bug")
    mock_client.get.assert_not_called()

@pytest.mark.asyncio
async def test_get_field_key(service, mock_client):
    # Mock /field/all
    resp = MagicMock()
    resp.json.return_value = {
        "err_code": 0,
        "data": [
            {"field_name": "优先级", "field_key": "field_prio", "field_alias": "priority"},
            {"field_name": "标题", "field_key": "name"}
        ]
    }
    resp.raise_for_status = MagicMock()
    mock_client.post.return_value = resp
    
    # By name
    k1 = await service.get_field_key("p1", "t1", "优先级")
    assert k1 == "field_prio"
    
    # By alias
    k2 = await service.get_field_key("p1", "t1", "priority")
    assert k2 == "field_prio"
    
    # By key itself (reverse lookup logic we added)
    k3 = await service.get_field_key("p1", "t1", "field_prio")
    assert k3 == "field_prio"
