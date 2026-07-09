"""
Model Registry for abstracting model type resolution.

Generated mappings are maintained in ``congressgov.services.core.model_registry_generated``
(regenerate with ``poetry run generate-registry``).

This module provides a central registry for resolving model classes and their
associated API mappings, reducing direct coupling between services and models.

Architecture Benefits:
- Service classes import only from model_registry
- Changes to model structure are isolated to this module
- Testable with mock registry
- Supports plugin architecture for custom models
- Clear separation between services and model layers

Usage Pattern:
    # Instead of importing models directly in services:
    from congressgov.models.entities.bill import Bill, Bills  # ❌ Tight coupling
    from congressgov.models.actions.action import Actions
    
    # Import from registry:
    from congressgov.services.core.model_registry import ModelRegistry  # ✅ Loose coupling
    
    # Get model dynamically:
    bill_model = ModelRegistry.get_model("Bill")
    actions_model = ModelRegistry.get_model("Actions")
"""

from __future__ import annotations
from typing import Type, Dict
import logging

from congressgov.services.core.model_registry_generated import MODEL_PATH_MAP

# NOTE: Configure module-level logger
logger = logging.getLogger(__name__)

# Hand-maintained aliases and legacy paths (override codegen map when keys collide)
HAND_MODEL_OVERRIDES: dict[str, str] = {
    "Term": "congressgov.models.entities.member",
    "Depiction": "congressgov.models.entities.member",
    "CongressSession": "congressgov.models.entities.congress",
    "CongressSessions": "congressgov.models.entities.congress",
    "Sponsor": "congressgov.models.entities.sponsor",
    "Sponsors": "congressgov.models.entities.sponsor",
    "Cosponsor": "congressgov.models.entities.sponsor",
    "Cosponsors": "congressgov.models.entities.sponsor",
    "OnBehalfOfSponsor": "congressgov.models.entities.sponsor",
    "OnBehalfOfSponsors": "congressgov.models.entities.sponsor",
    "CosponsorsRef": "congressgov.models.entities.sponsor",
    "TextVersionItem": "congressgov.models.entities.bill",
    "TextVersions": "congressgov.models.entities.bill",
    "TextVersionFormat": "congressgov.models.entities.bill",
    "TextVersionFormats": "congressgov.models.entities.bill",
    "Action": "congressgov.models.actions.action",
    "ActionsRef": "congressgov.models.actions.action",
    "RecordedVote": "congressgov.models.actions.vote",
    "RecordedVotes": "congressgov.models.actions.vote",
    "CalendarNumber": "congressgov.models.actions.calendar",
    "CommitteeRef": "congressgov.models.committees.committee",
    "CommitteeShortRef": "congressgov.models.committees.committee",
    "MatchingCommunication": "congressgov.models.communications.house_requirement",
    "MatchingCommunications": "congressgov.models.communications.house_requirement",
    "MemberVotes": "congressgov.models.communications.house_vote",
    "HouseVoteMembers": "congressgov.models.communications.house_vote",
    "CommitteeReports": "congressgov.models.documents.reports",
    "CommitteeReportText": "congressgov.models.documents.reports",
    "CommitteeReportTexts": "congressgov.models.documents.reports",
    "CommitteePrints": "congressgov.models.documents.prints",
    "CommitteePrintText": "congressgov.models.documents.prints",
    "CommitteePrintTexts": "congressgov.models.documents.prints",
    "CongressionalRecord": "congressgov.models.documents.congressional_record",
    "DailyCongressionalRecord": "congressgov.models.documents.congressional_record",
    "DailyCongressionalRecordIssue": "congressgov.models.documents.congressional_record",
    "DailyCongressionalRecordArticles": "congressgov.models.documents.congressional_record",
    "BoundCongressionalRecords": "congressgov.models.documents.bound_congressional_record",
    "Nominees": "congressgov.models.nominations.nomination",
    "Note": "congressgov.models.core.core",
    "Notes": "congressgov.models.core.core",
    "Law": "congressgov.models.core.core",
    "Laws": "congressgov.models.core.core",
    "Subject": "congressgov.models.core.core",
    "Subjects": "congressgov.models.core.core",
    "CBOCostEstimate": "congressgov.models.core.core",
    "CBOCostEstimates": "congressgov.models.core.core",
    "Summary": "congressgov.models.entities.bill",
    "Title": "congressgov.models.core.core",
    "Titles": "congressgov.models.core.core",
    "Model": "congressgov.models.base.model",
    "Pagination": "congressgov.models.base.model",
    "ApiEnvelope": "congressgov.models.base.model",
    "CountRef": "congressgov.models.base.types",
    "URL": "congressgov.models.base.types",
    "PolicyArea": "congressgov.models.base.types",
    "BillRef": "congressgov.models.base.references",
    "MemberRef": "congressgov.models.base.references",
    "SponsoredLegislation": "congressgov.models.entities.member",
    "SponsoredLegislationItem": "congressgov.models.entities.member",
    "CosponsoredLegislation": "congressgov.models.entities.member",
    "CosponsoredLegislationItem": "congressgov.models.entities.member",
    "AmendmentRef": "congressgov.models.base.references",
    "TreatyRef": "congressgov.models.base.references",
    "NominationRef": "congressgov.models.base.references",
}

# NOTE: Lazy-loaded model cache to avoid circular imports at module load time
_model_cache: Dict[str, Type] = {}


class ModelRegistry:
    """
    Central registry for model type resolution and API mappings.
    
    This registry provides a layer of indirection between services and models,
    allowing API services to work with models without direct imports.
    
    Features:
    - Lazy loading of model classes
    - Caching for performance
    - Support for custom model registration
    - Clear error messages for missing models
    
    Example:
        # Get a model class
        BillModel = ModelRegistry.get_model("Bill")
        
        # Register custom model
        ModelRegistry.register_model("CustomBill", CustomBillClass)
    """
    
    # ========================================================================
    # CORE MODEL RESOLUTION
    # ========================================================================
    
    @classmethod
    def get_model(cls, model_name: str) -> Type:
        """
        Get a model class by name with lazy loading.
        
        NOTE: Uses caching to avoid repeated imports.
        NOTE: Lazy loads on first access to avoid circular import issues.
        
        Args:
            model_name: Name of the model class (e.g., "Bill", "Actions", "Member")
            
        Returns:
            Model class
            
        Raises:
            KeyError: If model name is not recognized
            ImportError: If model cannot be imported
            
        Example:
            BillModel = ModelRegistry.get_model("Bill")
            bill = BillModel(**data)
        """
        # Check cache first
        if model_name in _model_cache:
            return _model_cache[model_name]
        
        # Lazy load and cache
        try:
            model_class = cls._import_model(model_name)
            _model_cache[model_name] = model_class
            return model_class
        except Exception as e:
            available = cls.list_available_models()
            raise KeyError(
                f"Model '{model_name}' not found. "
                f"Available models: {', '.join(available)}. "
                f"Error: {str(e)}"
            )
    
    @classmethod
    def _import_model(cls, model_name: str) -> Type:
        """
        Import a model class dynamically based on naming conventions.
        
        NOTE: This method understands the project's model organization structure.
        
        Args:
            model_name: Name of the model class
            
        Returns:
            Model class
            
        Raises:
            ImportError: If model cannot be imported
        """
        all_models = {**MODEL_PATH_MAP, **HAND_MODEL_OVERRIDES}
        
        # Import the model
        if model_name in all_models:
            module_path = all_models[model_name]
            try:
                module = __import__(module_path, fromlist=[model_name])
                return getattr(module, model_name)
            except (ImportError, AttributeError) as e:
                raise ImportError(
                    f"Could not import {model_name} from {module_path}: {str(e)}"
                )
        
        raise KeyError(f"Model '{model_name}' is not registered in ModelRegistry")
    
    @classmethod
    def register_model(cls, model_name: str, model_class: Type) -> None:
        """
        Register a custom model class.
        
        NOTE: This is an advanced feature for plugins, testing, or custom extensions.
        NOTE: Most users should rely on built-in model registration via _import_model().
        
        Useful for:
        - Testing with mock models
        - Adding custom model classes for extensions
        - Plugin architecture implementations
        
        Args:
            model_name: Name to register the model under
            model_class: Model class to register
            
        Example:
            ModelRegistry.register_model("CustomBill", MyCustomBillClass)
            custom = ModelRegistry.get_model("CustomBill")
        """
        _model_cache[model_name] = model_class
        logger.info(f"Registered custom model: {model_name}")
    
    @classmethod
    def list_available_models(cls) -> list[str]:
        """
        List all available model names.
        
        Returns:
            List of model names that can be requested
            
        Example:
            models = ModelRegistry.list_available_models()
            print(f"Available models: {', '.join(models)}")
        """
        return sorted(set(MODEL_PATH_MAP) | set(HAND_MODEL_OVERRIDES))
    
    @classmethod
    def clear_cache(cls) -> None:
        """
        Clear all cached models.
        
        Useful for testing or when models need to be reloaded.
        
        Example:
            ModelRegistry.clear_cache()
        """
        _model_cache.clear()
        logger.info("Cleared ModelRegistry cache")

