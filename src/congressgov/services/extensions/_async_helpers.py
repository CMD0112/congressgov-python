"""Shared helpers for async model extension methods."""

from __future__ import annotations

import json
from typing import Any, Callable

from congressgov.models.base.model import ApiEnvelope
from congressgov.services.core.async_api_service import AsyncApiService


async def resolve_client(target: Any, client: Any = None) -> Any:
    return await AsyncApiService._resolve_client(target, client)


async def call_api_async(
    fetch_fn: Callable,
    model_cls: type,
    *,
    client: Any,
    **params: Any,
) -> Any:
    resp = await fetch_fn(client=client, **params)
    api_env = ApiEnvelope.model_validate(json.loads(resp.content))
    return model_cls.model_validate(api_env.data)
