"""Tests for OpenAPI merge-time sanitization."""

from __future__ import annotations

import copy

import yaml

from codegen.scripts.merge_openapi_annotations import (
    OUTPUT_SPEC,
    _sanitize_openapi_document,
    main as merge_main,
    sanitize_openapi_spec,
)


def test_string_boolean_enum_becomes_boolean() -> None:
    doc = {
        "components": {
            "parameters": {
                "currentMember": {
                    "name": "currentMember",
                    "in": "query",
                    "schema": {"type": "string", "enum": [True, False]},
                }
            }
        }
    }
    _sanitize_openapi_document(doc)
    schema = doc["components"]["parameters"]["currentMember"]["schema"]
    assert schema["type"] == "boolean"
    assert schema["enum"] == [True, False]


def test_items_single_ref_collapsed() -> None:
    doc = {
        "components": {
            "schemas": {
                "Example": {
                    "type": "array",
                    "items": [{"$ref": "#/components/schemas/Foo"}],
                }
            }
        }
    }
    _sanitize_openapi_document(doc)
    items = doc["components"]["schemas"]["Example"]["items"]
    assert items == {"$ref": "#/components/schemas/Foo"}


def test_valid_string_enum_unchanged() -> None:
    doc = {
        "schema": {
            "type": "string",
            "enum": ["house", "senate", "joint"],
        }
    }
    before = copy.deepcopy(doc)
    _sanitize_openapi_document(doc)
    assert doc == before


def test_array_without_items_gets_object_items() -> None:
    doc = {"schema": {"type": "array"}}
    _sanitize_openapi_document(doc)
    assert doc["schema"]["items"] == {"type": "object"}


def test_schema_name_collision_renamed() -> None:
    doc = {
        "components": {
            "schemas": {
                "treaty": {"type": "object", "properties": {"n": {"type": "string"}}},
                "Treaty": {
                    "type": "object",
                    "properties": {
                        "treaties": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/treaty"},
                        }
                    },
                },
            }
        }
    }
    sanitize_openapi_spec(doc)
    schemas = doc["components"]["schemas"]
    assert "treaty" not in schemas
    assert "TreatyItem" in schemas
    assert schemas["Treaty"]["properties"]["treaties"]["items"]["$ref"].endswith("/TreatyItem")


def test_path_parameter_marked_required() -> None:
    doc = {
        "paths": {
            "/foo/{year}": {
                "get": {
                    "parameters": [
                        {"name": "year", "in": "path", "required": False, "schema": {"type": "integer"}}
                    ]
                }
            }
        }
    }
    sanitize_openapi_spec(doc)
    param = doc["paths"]["/foo/{year}"]["get"]["parameters"][0]
    assert param["required"] is True


def test_merged_spec_current_member_is_boolean() -> None:
    exit_code = merge_main()
    assert exit_code == 0
    text = OUTPUT_SPEC.read_text(encoding="utf-8")
    if text.startswith("#"):
        text = text.split("\n", 1)[1]
    merged = yaml.safe_load(text)
    schema = merged["components"]["parameters"]["currentMember"]["schema"]
    assert schema["type"] == "boolean"
