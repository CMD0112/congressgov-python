"""
Core service module - Backward compatibility facade.

This module maintains backward compatibility by re-exporting all classes
from the newly organized sub-modules. New code should import directly from:
- congressgov.services.core.api_service (ApiService, ExpansionResult)
- congressgov.services.core.dispatch (Dispatch, get_classes_dict)
- congressgov.services.core.database (SQLAlchemyHelper)
- congressgov.services.core.storage (StorageManager, UnifiedStorage, etc.)

Migration Guide:
    OLD:
        from congressgov.services.core.service import ApiService, StorageManager
    
    NEW (recommended):
        from congressgov.services.core.api_service import ApiService
        from congressgov.services.core.storage import StorageManager
    
    CURRENT (still works):
        from congressgov.services.core.service import ApiService, StorageManager

This facade will be maintained for backward compatibility during migration.
"""

from __future__ import annotations

import warnings

# API Service classes
from .api_service import (
    ApiService,
    ExpansionResult,
)

# Dispatch classes
from .dispatch import (
    Dispatch,
    get_classes_dict,
)

# Database classes
from .database import (
    SQLAlchemyHelper,
    get_base_registry,
)

# Storage classes
from .storage import (
    StorageManager,
    StorageBackendType,
    StorageBackend,
    FileStorageBackend,
    InMemoryStorageBackend,
    StorageFactory,
    SQLStorageAdapter,
    UnifiedStorage,
)

__all__ = [
    # API Service
    'ApiService',
    'ExpansionResult',
    
    # Dispatch
    'Dispatch',
    'get_classes_dict',
    
    # Database
    'SQLAlchemyHelper',
    'get_base_registry',
    
    # Storage
    'StorageManager',
    'StorageBackendType',
    'StorageBackend',
    'FileStorageBackend',
    'InMemoryStorageBackend',
    'StorageFactory',
    'SQLStorageAdapter',
    'UnifiedStorage',
]


# Not wired up yet - kept here so a future version can enable deprecation
# warnings without redesigning the facade. Deprecation plan: (1) current
# state, full compatibility, no warnings; (2) add warnings by uncommenting
# the call below; (3) move to a private _service.py with an import
# redirect; (4) remove the facade entirely.
def _issue_deprecation_warning():
    """Warn that importing from service.py is deprecated (currently unused)."""
    warnings.warn(
        "Importing from congressgov.services.core.service is deprecated. "
        "Please import from specific modules:\n"
        "  - congressgov.services.core.api_service (ApiService, ExpansionResult)\n"
        "  - congressgov.services.core.dispatch (Dispatch, get_classes_dict)\n"
        "  - congressgov.services.core.database (SQLAlchemyHelper)\n"
        "  - congressgov.services.core.storage (StorageManager, UnifiedStorage, etc.)",
        DeprecationWarning,
        stacklevel=3
    )

# Uncomment the following line in a future version to enable deprecation warnings:
# _issue_deprecation_warning()
