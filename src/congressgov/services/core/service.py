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

# ============================================================================
# RE-EXPORTS FOR BACKWARD COMPATIBILITY
# ============================================================================

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

# ============================================================================
# PUBLIC API
# ============================================================================

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


# ============================================================================
# DEPRECATION HELPERS
# ============================================================================
# 
# NOTE: Deprecation Path for congressgov.services.core.service
# ====================================================
# This module is a backward compatibility facade that will be maintained
# for the foreseeable future. Direct imports from specific modules are
# preferred for new code:
#
#   Preferred (new code):
#     from congressgov.services.core.api_service import ApiService
#     from congressgov.services.core.dispatch import Dispatch
#     from congressgov.services.core.storage import StorageManager
#
#   Supported (backward compatibility):
#     from congressgov.services.core.service import ApiService, Dispatch, StorageManager
#
# Future deprecation plan:
#   1. Current state: Full backward compatibility, no warnings
#   2. Version N+1: Add deprecation warnings (uncomment function below)
#   3. Version N+2: Move to private module (_service.py) with import redirect
#   4. Version N+3: Remove compatibility facade entirely
#
# To enable deprecation warnings in a future version, uncomment this function:

def _issue_deprecation_warning():
    """
    Issue deprecation warning for importing from service.py.
    
    NOTE: Currently disabled to maintain full backward compatibility.
    Enable this in a future version to encourage migration to new imports.
    """
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
