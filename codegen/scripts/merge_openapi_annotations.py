#!/usr/bin/env python3
"""
Merge x-* codegen annotations from openapi_spec_annotations.yaml onto the
official Congress.gov OpenAPI base spec. Writes codegen/config/openapi_spec.yaml.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import yaml

HTTP_METHODS = frozenset({"get", "post", "put", "patch", "delete", "head", "options", "trace"})
CONFIG_ROOT = Path(__file__).resolve().parents[1] / "config"
BASE_SPEC = CONFIG_ROOT / "congressgov_openapi_base.yaml"
OVERLAY_SPEC = CONFIG_ROOT / "openapi_spec_annotations.yaml"
OUTPUT_SPEC = CONFIG_ROOT / "openapi_spec.yaml"


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _is_boolean_enum(enum_values: object) -> bool:
    """True when enum is exactly YAML booleans true/false (invalid with type: string)."""
    return isinstance(enum_values, list) and set(enum_values) == {True, False}


def _sanitize_schema_object(schema: dict) -> None:
    """Fix schema objects that break openapi-python-client."""
    items = schema.get("items")
    if isinstance(items, list) and len(items) == 1:
        only = items[0]
        if isinstance(only, dict) and "$ref" in only:
            schema["items"] = only

    if schema.get("type") == "string" and _is_boolean_enum(schema.get("enum")):
        schema["type"] = "boolean"

    if schema.get("type") == "array" and not schema.get("items") and not schema.get("prefixItems"):
        schema["items"] = {"type": "object"}


def _sanitize_openapi_document(node: object) -> None:
    """Fix known Congress.gov spec quirks that break openapi-python-client."""
    if isinstance(node, dict):
        if "type" in node or "enum" in node or "items" in node:
            _sanitize_schema_object(node)
        for value in node.values():
            _sanitize_openapi_document(value)
    elif isinstance(node, list):
        for value in node:
            _sanitize_openapi_document(value)


def _update_schema_refs(node: object, renames: dict[str, str]) -> None:
    """Rewrite #/components/schemas/... references after schema renames."""
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/components/schemas/"):
            old_name = ref.rsplit("/", 1)[-1]
            if old_name in renames:
                node["$ref"] = f"#/components/schemas/{renames[old_name]}"
        for value in node.values():
            _update_schema_refs(value, renames)
    elif isinstance(node, list):
        for value in node:
            _update_schema_refs(value, renames)


def _sanitize_schema_name_collisions(doc: dict) -> None:
    """Rename camelCase schemas that collide with PascalCase wrappers in openapi-python-client."""
    schemas = doc.get("components", {}).get("schemas")
    if not isinstance(schemas, dict):
        return

    by_lower: dict[str, list[str]] = {}
    for name in schemas:
        by_lower.setdefault(name.lower(), []).append(name)

    renames: dict[str, str] = {}
    for names in by_lower.values():
        if len(names) < 2:
            continue
        pascal_names = [n for n in names if n[0].isupper()]
        camel_names = [n for n in names if n[0].islower()]
        if not camel_names or not pascal_names:
            continue
        base = pascal_names[0]
        for camel in camel_names:
            candidate = f"{base}Item"
            suffix = 0
            while candidate in schemas and candidate != camel:
                suffix += 1
                candidate = f"{base}Item{suffix}" if suffix else f"{base}Item"
            renames[camel] = candidate

    for old_name, new_name in renames.items():
        schemas[new_name] = schemas.pop(old_name)
    if renames:
        _update_schema_refs(doc, renames)


def _sanitize_path_parameters(doc: dict) -> None:
    """Path parameters must be required for openapi-python-client."""
    paths = doc.get("paths", {})
    if not isinstance(paths, dict):
        return

    def fix_params(params: object) -> None:
        if not isinstance(params, list):
            return
        for param in params:
            if isinstance(param, dict) and param.get("in") == "path":
                param["required"] = True
                param.pop("default", None)

    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue
        fix_params(path_item.get("parameters"))
        for method in HTTP_METHODS:
            op = path_item.get(method)
            if isinstance(op, dict):
                fix_params(op.get("parameters"))

    components_params = doc.get("components", {}).get("parameters")
    if isinstance(components_params, dict):
        for param in components_params.values():
            if isinstance(param, dict) and param.get("in") == "path":
                param["required"] = True
                schema = param.get("schema")
                if isinstance(schema, dict):
                    schema.pop("default", None)
                param.pop("default", None)


def sanitize_openapi_spec(doc: dict) -> None:
    """Apply all merge-time sanitizers to an OpenAPI document."""
    _sanitize_schema_name_collisions(doc)
    _sanitize_path_parameters(doc)
    _sanitize_openapi_document(doc)


def _is_extension_key(key: str) -> bool:
    return key.startswith("x-")


def _merge_operation_overlay(base_op: dict, overlay_op: dict) -> None:
    for key, value in overlay_op.items():
        if _is_extension_key(key):
            base_op[key] = copy.deepcopy(value)


def merge_specs(base: dict, overlay: dict) -> tuple[dict, list[str]]:
    merged = copy.deepcopy(base)
    base_paths = merged.setdefault("paths", {})
    overlay_paths = overlay.get("paths", {}) or {}

    unmatched: list[str] = []
    matched = 0

    for path, overlay_path_item in overlay_paths.items():
        if path not in base_paths:
            unmatched.append(path)
            continue

        base_path_item = base_paths[path]
        if not isinstance(overlay_path_item, dict):
            continue

        for method, overlay_op in overlay_path_item.items():
            if method not in HTTP_METHODS or not isinstance(overlay_op, dict):
                continue
            base_op = base_path_item.get(method)
            if not isinstance(base_op, dict):
                unmatched.append(f"{path} [{method.upper()}]")
                continue
            _merge_operation_overlay(base_op, overlay_op)
            matched += 1

    return merged, unmatched, matched


def main() -> int:
    if not BASE_SPEC.exists():
        print(f"ERROR: Base spec not found: {BASE_SPEC}", file=sys.stderr)
        return 1
    if not OVERLAY_SPEC.exists():
        print(f"ERROR: Overlay spec not found: {OVERLAY_SPEC}", file=sys.stderr)
        return 1

    base = _load_yaml(BASE_SPEC)
    sanitize_openapi_spec(base)
    overlay = _load_yaml(OVERLAY_SPEC)
    merged, unmatched, matched = merge_specs(base, overlay)
    sanitize_openapi_spec(merged)

    header = (
        "# Merged OpenAPI spec: official Congress.gov base + codegen annotations overlay.\n"
        "# Regenerate: poetry run merge-openapi-spec\n"
        "# Base: codegen/config/congressgov_openapi_base.yaml\n"
        "# Overlay: codegen/config/openapi_spec_annotations.yaml\n"
    )
    body = yaml.dump(
        merged,
        default_flow_style=False,
        sort_keys=False,
        allow_unicode=True,
        width=120,
    )
    OUTPUT_SPEC.write_text(header + body, encoding="utf-8")

    print(f"Wrote {OUTPUT_SPEC} ({matched} operation overlay(s) applied)")
    if unmatched:
        print("WARNING: Unmatched overlay paths (not in base spec):", file=sys.stderr)
        for item in unmatched:
            print(f"  - {item}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
