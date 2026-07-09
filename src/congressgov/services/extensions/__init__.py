"""
Dynamic Method Extensions for Model Classes

This package contains dynamically-registered methods for model classes.
Methods are automatically registered when this package is imported.

Structure:
    extensions/
        __init__.py          # Auto-registration (this file)
        _registry.py         # Base registry decorators and utilities
        _query_builder.py    # Generic query builder with enum support
        _template.py         # Template for creating new extensions
        members.py           # Methods for Members model
        bill.py              # Methods for Bills model
        committees.py        # Methods for Committees model (future)

Features:
    - Generic query builder eliminates custom query classes
    - Enum-based field mappings enable shorthand queries (e.g., state="CA")
    - Automatic registration on import
    - Full type safety and IDE support

Usage:
    # Import congressgov (automatically registers all extensions)
    from congressgov import Member
    
    # Extensions are now available
    members = member_service.get_current_roster()
    
    # Shorthand queries work automatically (via StateCode enum)
    ca_members = members['house_members'].filter(state="CA")  # Matches "California"

Adding New Extensions:
    1. Copy template: cp _template.py mymodel.py
    2. Replace placeholders in the file
    3. Add enum mappings if needed: FieldMapping(enum_class=YourEnum)
    4. Import in this __init__.py
"""

# Import registry and query builder utilities
from ._registry import register_method, get_registered_models
from ._query_builder import (
    CollectionQuery,
    QueryConfig,
    FieldMapping,
    enum_expander,
    create_query_builder
)

# ========================================
# AUTO-IMPORT ALL EXTENSION MODULES
# ========================================
# Each module registers its methods on import

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

# Async API extensions (register *_async methods on models)
import importlib as _importlib

_importlib.import_module("congressgov.services.extensions.async")

# Future extensions:
# from . import congresses  # noqa: F401
from . import house_votes  # noqa: F401
from . import url_follow  # noqa: F401

__all__ = [
    # Registry
    'register_method',
    'get_registered_models',
    
    # Query Builder
    'CollectionQuery',
    'QueryConfig',
    'FieldMapping',
    'enum_expander',
    'create_query_builder',
]

# NOTE: To add a new extension module:
# 1. Create the file (e.g., bills.py) using _template.py
# 2. Add field mappings with enums for shorthand support
# 3. Add import above
# 4. Methods are automatically registered

