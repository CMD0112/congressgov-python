"""
API Service module for congressgov.services functionality.

This module provides:
- ApiService: Base class for API services with client resolution and expansion
- ExpansionResult: Dataclass for detailed expansion results

Best Practices:
- Client resolution with fallback logic
- Deep copying with Pydantic model awareness
- Attribute expansion by fetching additional data from API
"""

from __future__ import annotations

from typing import Any, Optional, Union
import json
import logging
from copy import deepcopy
from dataclasses import dataclass

from congressgov.models.base.model import ApiEnvelope
from congressgov.services.api_format import resolve_response_format
from congressgov.services.config import MAX_EXPANSION_ATTRIBUTES
from congressgov.services.core.expansion_helpers import extract_parameters_from_target

# NOTE: Configure module-level logger
logger = logging.getLogger(__name__)


@dataclass
class ExpansionResult:
    """
    Result of an attribute expansion operation.
    
    Attributes:
        success: Whether expansion completed successfully
        expanded_target: The target object with expanded attributes
        errors: List of (attribute_name, error) tuples for failed expansions
    """
    success: bool
    expanded_target: Any
    errors: list[tuple[str, Exception]]


class ApiService:
    """
    Base service class for all congressgov.services API wrappers.
    
    Provides common functionality for:
    - Client resolution with fallback logic
    - Attribute expansion by fetching additional data from API
    - Deep copying with Pydantic model awareness
    
    Example:
        service = ApiService()
        expanded = service.expand(
            target=my_bill,
            client=api_client,
            mapping={"text": {fetch_text: TextModel}},
            parameters=["congress", "billType", "billNumber"]
        )
    """

    @staticmethod
    def _resolve_client(target: Any, provided_client: Optional[Any] = None) -> Any:
        """
        Resolve the client parameter using fallback logic.
        
        Resolution order:
        1. Explicitly provided client parameter
        2. Client attribute on target object
        3. Raise ValueError if no client found
        
        Args:
            target: Object that may have a client attribute
            provided_client: Explicitly provided client (takes precedence)
            
        Returns:
            Resolved client instance
            
        Raises:
            ValueError: If no client can be resolved
        """
        # NOTE: Check provided client first (highest priority)
        if provided_client is not None:
            return provided_client
        
        # NOTE: Fall back to target's client attribute
        if target is not None:
            target_client = getattr(target, 'client', None)
            if target_client is not None:
                return target_client

            # NOTE: Items in a collection may inherit client from the parent Members/Bills/etc.
            parent = getattr(target, '_parent_collection', None)
            if parent is not None:
                parent_client = getattr(parent, 'client', None)
                if parent_client is not None:
                    return parent_client
        
        from congressgov.services.exceptions import ClientNotFoundError

        raise ClientNotFoundError(
            "No client available. Either provide a client parameter or ensure the target "
            "object has a 'client' attribute set."
        )

    @staticmethod
    def resolve_format(format_: str | Any | None, enum_cls: type) -> Any:
        """Resolve optional caller *format_* to a generated client format enum."""
        return resolve_response_format(format_, enum_cls)

    @staticmethod
    def _create_deep_copy(target: Any) -> Any:
        """
        Create deep copy of target object with special handling for Pydantic models.
        
        NOTE: Pydantic models require special handling - client and session attributes
        must be temporarily removed before copying to avoid serialization issues.
        
        Args:
            target: Object to deep copy
            
        Returns:
            Deep copy of target with client/session attributes preserved
        """
        # NOTE: Handle Pydantic models with model_copy method
        if hasattr(target, 'model_copy'):
            # Store attributes that can't be serialized
            saved_attrs = {
                'client': getattr(target, 'client', None),
                'session': getattr(target, 'session', None)
            }
            
            # Temporarily remove non-serializable attributes
            for attr_name, attr_value in saved_attrs.items():
                if attr_value is not None and hasattr(target, attr_name):
                    delattr(target, attr_name)
            
            try:
                # Create deep copy using Pydantic's method
                copied_target = target.model_copy(deep=True)
            finally:
                # Restore attributes to original object
                for attr_name, attr_value in saved_attrs.items():
                    if attr_value is not None:
                        setattr(target, attr_name, attr_value)
            
            # Copy attributes to new object
            for attr_name, attr_value in saved_attrs.items():
                if attr_value is not None:
                    setattr(copied_target, attr_name, attr_value)
            
            return copied_target
        
        # NOTE: Handle regular objects with __dict__
        else:
            # Exclude non-serializable attributes
            exclude_attrs = {'client', '_client', 'session', '_session'}
            state = {
                k: v for k, v in getattr(target, '__dict__', {}).items()
                if k not in exclude_attrs
            }
            
            # Deep copy the state
            copied_state = deepcopy(state)
            
            # Create new instance without calling __init__
            copied_target = object.__new__(type(target))
            copied_target.__dict__.update(copied_state)
            
            # Restore non-serializable attributes (shallow copy)
            for attr in ['client', 'session']:
                if hasattr(target, attr):
                    setattr(copied_target, attr, getattr(target, attr))
            
            return copied_target

    @staticmethod
    def _extract_parameters(
        target: Any,
        parameters: Union[list[str], dict[str, Union[str, list[str]]], None],
        normalize_params: Optional[list[str]] = None
    ) -> dict[str, Any]:
        """
        Extract and validate required parameters from target object.
        
        NOTE: Supports parameter aliases for flexibility in attribute naming.
        
        Args:
            target: Object to extract parameters from
            parameters: Parameter specification - can be:
                - List of strings: parameter names (API param = attribute name)
                - Dict: {api_param: attribute_name} or {api_param: [aliases]}
                - None: No parameters to extract
            normalize_params: List of parameter names to normalize to lowercase
            
        Returns:
            Dictionary of extracted parameter values
            
        Raises:
            ValueError: If any required parameter is missing or empty
        """
        return extract_parameters_from_target(
            target,
            parameters,
            normalize_params=normalize_params,
        )

    @staticmethod
    def _expand_single_attribute(
        target: Any,
        attr_name: str,
        mapping_entry: dict[Any, Any],
        client: Any,
        extracted_parameters: dict[str, Any],
        **kwargs: Any
    ) -> tuple[bool, Optional[Exception]]:
        """
        Expand a single attribute by fetching data from the API.
        
        Args:
            target: Target object to expand
            attr_name: Name of attribute to expand
            mapping_entry: Dict with single key-value pair {api_function: model_class}
            client: API client instance
            extracted_parameters: Parameters to pass to API function
            kwargs: Additional keyword arguments for API function
            
        Returns:
            Tuple of (success: bool, error: Optional[Exception])
        """
        try:
            # NOTE: Extract API function and model class from mapping
            # Mapping entry format: {api_function: model_class}
            api_function, model_class = next(iter(mapping_entry.items()))

            from congressgov.services.core.expansion_helpers import is_loaded_related_attribute
            from congressgov.services.core.request_store import fetch_options

            force_fetch = bool(kwargs.pop("force_fetch", False))
            current = getattr(target, attr_name, None)
            if not force_fetch and is_loaded_related_attribute(current, model_class):
                if getattr(current, "client", None) is None:
                    current.client = client
                setattr(target, attr_name, current)
                return True, None

            # NOTE: Call API function to fetch data
            with fetch_options(force_fetch=force_fetch):
                response = api_function(client=client, **extracted_parameters, **kwargs)
            
            # NOTE: Parse response through API envelope
            json_response = json.loads(response.content)
            api_envelope = ApiEnvelope.model_validate(json_response)
            
            # NOTE: Validate data as model instance
            model_instance = model_class.model_validate(api_envelope.data)
            
            # NOTE: Set expanded attribute on target
            setattr(target, attr_name, model_instance)
            
            return True, None
            
        except Exception as e:
            # NOTE: Log warning but don't raise - allow other attributes to expand
            logger.warning(f"Failed to expand attribute '{attr_name}': {e}")
            return False, e

    def expand(
        self,
        target: Any,
        client: Optional[Any] = None,
        mapping: Optional[dict[str, dict[Any, Any]]] = None,
        parameters: Union[list[str], dict[str, Union[str, list[str]]], None] = None,
        attributes: Optional[list[str]] = None,
        normalize_params: Optional[list[str]] = None,
        entity_name: str = "target",
        return_detailed_result: bool = False,
        **kwargs: Any
    ) -> Union[Any, ExpansionResult]:
        """
        Expand attributes of a target object by fetching additional data from the API.
        
        NOTE: Creates a deep copy of the target before expansion to avoid mutating original.
        NOTE: Failed expansions log warnings but don't prevent other attributes from expanding.
        
        Args:
            target: Object to expand (will be deep copied)
            client: API client (or use target's client attribute)
            mapping: Dict mapping attribute names to {api_function: model_class}
            parameters: Parameters to extract from target for API calls
            attributes: Specific attributes to expand (None = all in mapping)
            normalize_params: Parameter names to normalize to lowercase
            entity_name: Entity name for error messages (default: "target")
            return_detailed_result: If True, return ExpansionResult with error details
            kwargs: Additional keyword arguments passed to API functions
            
        Returns:
            Expanded target object (or ExpansionResult if return_detailed_result=True)
            
        Raises:
            ClientNotFoundError: If client cannot be resolved
            ValueError: If required parameters are missing
            
        Example:
            expanded_bill = service.expand(
                target=bill,
                client=api_client,
                mapping={
                    "text": {api.fetch_bill_text: TextModel},
                    "actions": {api.fetch_bill_actions: ActionsModel}
                },
                parameters=["congress", "billType", "billNumber"]
            )
        """
        # NOTE: Create deep copy to avoid mutating original object
        expanded_target = self._create_deep_copy(target)
        
        # NOTE: Resolve client using fallback logic
        client = self._resolve_client(target, client)
        
        # NOTE: Extract and validate required parameters
        extracted_parameters = self._extract_parameters(
            target, parameters, normalize_params
        )
        
        # NOTE: Determine which attributes to expand
        if mapping is None:
            mapping = {}
        
        attributes_to_expand = attributes if attributes is not None else list(mapping.keys())
        
        # NOTE: Validate attribute count against configuration limit
        if len(attributes_to_expand) > MAX_EXPANSION_ATTRIBUTES:
            logger.warning(
                f"Attempting to expand {len(attributes_to_expand)} attributes, "
                f"which exceeds the configured limit of {MAX_EXPANSION_ATTRIBUTES}. "
                f"Proceeding anyway but consider expanding fewer attributes for better performance."
            )
        
        # NOTE: Expand each attribute independently
        errors = []
        for attr_name in attributes_to_expand:
            if attr_name not in mapping:
                continue  # Skip attributes not in mapping
            
            success, error = self._expand_single_attribute(
                target=expanded_target,
                attr_name=attr_name,
                mapping_entry=mapping[attr_name],
                client=client,
                extracted_parameters=extracted_parameters,
                **kwargs
            )
            
            if not success and error is not None:
                errors.append((attr_name, error))
        
        # NOTE: Return detailed result if requested
        if return_detailed_result:
            return ExpansionResult(
                success=len(errors) == 0,
                expanded_target=expanded_target,
                errors=errors
            )
        
        return expanded_target



