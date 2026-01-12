import pytest
from unittest.mock import AsyncMock
from src.providers.project.metadata import FieldMetadataProvider
from src.schemas.project import BaseResponse, FieldDefinition


@pytest.fixture
def mock_api():
    return AsyncMock()


@pytest.mark.asyncio
async def test_get_field_mappings_caching(mock_api):
    provider = FieldMetadataProvider(api_client=mock_api)
    project_key = "PROJ_1"

    mock_fields = [
        FieldDefinition(
            field_key="field_1", field_name="Priority", field_type_key="select"
        ),
        FieldDefinition(
            field_key="field_2", field_name="Status", field_type_key="text"
        ),
    ]
    mock_api.get_project_fields.return_value = BaseResponse(code=0, data=mock_fields)

    # First call - should call API
    mapping1 = await provider.get_field_mappings(project_key)
    assert mapping1["field_1"] == "Priority"
    assert mock_api.get_project_fields.call_count == 1

    # Second call - should use cache
    mapping2 = await provider.get_field_mappings(project_key)
    assert mapping2 == mapping1
    assert mock_api.get_project_fields.call_count == 1


@pytest.mark.asyncio
async def test_translate_keys(mock_api):
    provider = FieldMetadataProvider(api_client=mock_api)
    project_key = "PROJ_1"

    mock_api.get_project_fields.return_value = BaseResponse(
        code=0,
        data=[
            FieldDefinition(
                field_key="field_1", field_name="Priority", field_type_key="select"
            )
        ],
    )

    raw_data = {"field_1": "High", "name": "Task 1"}
    translated = await provider.translate_keys(project_key, raw_data)

    assert translated == {"Priority": "High", "name": "Task 1"}


@pytest.mark.asyncio
async def test_get_reverse_mappings(mock_api):
    provider = FieldMetadataProvider(api_client=mock_api)
    project_key = "PROJ_1"

    mock_api.get_project_fields.return_value = BaseResponse(
        code=0,
        data=[
            FieldDefinition(
                field_key="field_1", field_name="Priority", field_type_key="select"
            )
        ],
    )

    rev = await provider.get_reverse_mappings(project_key)
    assert rev == {"Priority": "field_1"}
