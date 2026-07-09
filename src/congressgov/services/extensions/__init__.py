"""
Query and convenience methods for model classes, attached at import time via
`_registry.register_method` rather than defined on the models themselves.
This keeps `congressgov.models` limited to Pydantic validation while entity
modules here own filtering, chaining, and per-entity helpers.

To add a new extension: copy `_template.py`, fill in the placeholders, and
import the new module below.
"""

from ._registry import register_method, get_registered_models
from ._query_builder import (
    CollectionQuery,
    QueryConfig,
    FieldMapping,
    enum_expander,
    create_query_builder
)

# Importing each module registers its methods as a side effect.
from . import collections_registry  # noqa: F401 — __iter__, __len__, … on collections

from . import members  # noqa: F401
from . import sponsorship_legislation  # noqa: F401
from . import bill  # noqa: F401
from . import amendments  # noqa: F401
from . import actions  # noqa: F401
from . import cosponsors  # noqa: F401
from . import committees  # noqa: F401
from . import committee_meetings  # noqa: F401
from . import committee_prints  # noqa: F401
from . import committee_reports  # noqa: F401
from . import hearings  # noqa: F401
from . import house_communications  # noqa: F401
from . import senate_communications  # noqa: F401
from . import nominations  # noqa: F401
from . import summaries  # noqa: F401
from . import treaties  # noqa: F401
from . import congress  # noqa: F401

# Registers *_async counterparts of the sync methods above.
import importlib as _importlib

_importlib.import_module("congressgov.services.extensions.async")

from . import house_votes  # noqa: F401
from . import url_follow  # noqa: F401

__all__ = [
    'register_method',
    'get_registered_models',
    'CollectionQuery',
    'QueryConfig',
    'FieldMapping',
    'enum_expander',
    'create_query_builder',
]

