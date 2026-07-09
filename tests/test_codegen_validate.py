"""Codegen spec validation tests."""

from pathlib import Path

from codegen.processors.spec_parser import SpecParser


SPEC_PATH = Path("codegen/config/openapi_spec.yaml")
ANNOTATIONS_PATH = Path("codegen/config/openapi_spec_annotations.yaml")


def test_merged_spec_has_pilot_entities() -> None:
    parser = SpecParser()
    parser.load_spec(SPEC_PATH)
    entities = parser.parse_entities()
    mappings_path = Path("codegen/config/entity_mappings.yaml")
    parser.apply_entity_mapping_fallback(mappings_path)
    names = set(entities.keys())
    assert "Bill" in names
    assert "Member" in names
    assert "Amendment" in names
    assert "Committee" in names


def test_bill_primary_endpoint_metadata() -> None:
    parser = SpecParser()
    parser.load_spec(SPEC_PATH)
    entities = parser.parse_entities()
    bill = entities["Bill"]
    assert bill.primary_endpoint is not None
    assert bill.primary_endpoint.api_function == "bill_details_sync"
    assert "bill_type" in bill.primary_endpoint.python_params
