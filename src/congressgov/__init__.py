"""
congressgov — Python SDK for the Congress.gov API.

Canonical import path (matches the PyPI distribution name):

    from congressgov import Bill, Member, get_client_from_env

Async services:

    from congressgov.async_api import AsyncBill

Namespaces (1.2+, explicit imports):

    from congressgov.services import Bill, get_client_from_env
    from congressgov.models import Bill as BillModel
    from congressgov.client import AuthenticatedClient

Low-level HTTP client (advanced):

    from congressgov.client import AuthenticatedClient
"""

from __future__ import annotations

import os
from typing import Any

# Suppress legacy-namespace warning when loading via this facade.
os.environ.setdefault("CONGRESSGOV_FACADE_IMPORT", "1")

import congressgov.services as _services  # noqa: E402

__version__ = _services.__version__

# Re-export public API from services (including lazy optional extras via __getattr__).
__all__ = list(_services.__all__)


def __getattr__(name: str) -> Any:
    return getattr(_services, name)
