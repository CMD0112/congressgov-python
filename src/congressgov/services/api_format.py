"""Resolve Congress.gov ``format`` query parameters for generated client enums."""

from __future__ import annotations

from enum import Enum
from typing import TypeVar

T = TypeVar("T", bound=Enum)


def resolve_response_format(format_: str | T | None, enum_cls: type[T]) -> T:
    """Default to JSON when service callers omit *format_*."""
    if format_ is None:
        return enum_cls.JSON
    if isinstance(format_, str):
        return enum_cls(format_.lower())
    return format_


def ensure_format_kwarg(
    kwargs: dict,
    enum_cls: type[T],
    key: str = "format_",
) -> dict:
    """Return *kwargs* with *key* resolved (for ``**kwargs`` client calls)."""
    if key in kwargs:
        kwargs = dict(kwargs)
        kwargs[key] = resolve_response_format(kwargs[key], enum_cls)
    return kwargs


def resolve_chamber(chamber: str | T, enum_cls: type[T]) -> T:
    """Coerce service chamber strings to generated client chamber enums."""
    if isinstance(chamber, enum_cls):
        return chamber
    return enum_cls(str(chamber).lower())
