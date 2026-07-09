from __future__ import annotations
from datetime import date, datetime
from typing import Any, Dict, Type, Optional

Json = Dict[str, Any]
Spec = Dict[str, Any]  # mapping spec type alias

def _build_spec(cls):
    return {key: key for key in cls.__annotations__.keys()}

def _get(d: Json, key: str, default=None):
    # allow dotted paths like "meta.updated.at"
    cur = d
    for part in key.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur

def _to_date(x: Any) -> Optional[date]:
    if x is None:
        return None
    if isinstance(x, date) and not isinstance(x, datetime):
        return x
    # be permissive: ISO or datetime-like
    try:
        return datetime.fromisoformat(str(x)).date()
    except Exception:
        return None

def _instantiate_with_kwargs_or_setattr(cls: Type, kwargs: Dict[str, Any]):
    """
    Try __init__(**kwargs). If that fails (e.g., custom Model with no kwargs),
    create cls() and setattr attributes/properties instead.
    """
    try:
        return cls(**kwargs)
    except Exception:
        obj = cls()
        for k, v in kwargs.items():
            setattr(obj, k, v)
        return obj

def from_json_spec(cls: Type, data: Json, spec: Spec = None):
    """
    Spec entry forms:
      - attr: "json_key"
      - attr: ("json_key", converter_fn)
      - attr: (NestedCls, nested_spec)
      - attr: ("json_key", NestedCls, nested_spec)        # nested dict
      - attr: ("json_key", [NestedCls, nested_spec])      # list of nested dicts
    """
    
    if spec is None:
        spec = _build_spec(cls)
    
    kwargs: Dict[str, Any] = {}

    for attr, rule in spec.items():
        # 1) Simple string: rename
        if isinstance(rule, str):
            kwargs[attr] = _get(data, rule)

        # 2) Tuple with many shapes
        elif isinstance(rule, tuple):
            if len(rule) == 2 and callable(rule[1]) and isinstance(rule[0], str):
                # ("json_key", converter)
                raw = _get(data, rule[0])
                kwargs[attr] = rule[1](raw)

            elif len(rule) == 2 and isinstance(rule[0], type):
                # (NestedCls, nested_spec) — nested from same dict
                NestedCls, nested_spec = rule
                kwargs[attr] = from_json_spec(NestedCls, data, nested_spec)

            elif len(rule) == 3 and isinstance(rule[0], str) and isinstance(rule[1], type):
                # ("json_key", NestedCls, nested_spec) — nested from sub-dict
                sub = _get(data, rule[0]) or {}
                NestedCls, nested_spec = rule[1], rule[2]
                kwargs[attr] = None if sub in (None, {}) else from_json_spec(NestedCls, sub, nested_spec)

            elif len(rule) == 2 and isinstance(rule[1], list) and len(rule[1]) == 2 and isinstance(rule[0], str):
                # ("json_key", [NestedCls, nested_spec]) — list of nested
                sub_list = _get(data, rule[0]) or []
                NestedCls, nested_spec = rule[1]
                if sub_list is None:
                    kwargs[attr] = None
                else:
                    kwargs[attr] = [from_json_spec(NestedCls, item, nested_spec) for item in sub_list]

            else:
                raise ValueError(f"Unrecognized mapping rule for {attr}: {rule!r}")

        else:
            raise ValueError(f"Unrecognized mapping rule type for {attr}: {type(rule)}")

    return _instantiate_with_kwargs_or_setattr(cls, kwargs)


# Note: This file contains utility functions, not Pydantic models, so no model_rebuild() calls are needed
