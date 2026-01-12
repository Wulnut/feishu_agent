import pytest
from src.schemas.project import BaseResponse, FieldDefinition, FieldOption


def test_field_definition_parsing():
    raw = {
        "code": 0,
        "msg": "success",
        "data": [
            {
                "field_key": "field_123",
                "field_name": "Priority",
                "field_type_key": "single_select",
                "options": [
                    {"label": "High", "value": "opt_1"},
                    {"label": "Low", "value": "opt_2"},
                ],
            },
            {
                "field_key": "field_456",
                "field_name": "Due Date",
                "field_type_key": "date",
            },
        ],
    }

    resp = BaseResponse[list[FieldDefinition]].model_validate(raw)

    assert resp.is_success
    assert len(resp.data) == 2
    assert resp.data[0].field_name == "Priority"
    assert len(resp.data[0].options) == 2
    assert resp.data[0].options[0].label == "High"
    assert resp.data[1].field_name == "Due Date"
    assert resp.data[1].options == []


def test_field_definition_with_alias():
    raw = {
        "field_key": "field_789",
        "field_name": "Owner",
        "field_alias": "owner_alias",
        "field_type_key": "user",
    }
    field = FieldDefinition.model_validate(raw)
    assert field.field_alias == "owner_alias"
