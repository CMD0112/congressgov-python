"""
Async API Service module for congressgov.services functionality.

This module provides async versions of the core service functionality:
- AsyncApiService: Base class for async API services with client resolution and expansion
- Mirrors the sync ApiService class with async methods

Best Practices:
- Async client resolution with fallback logic
- Async attribute expansion by fetching additional data from API
- Deep copying with Pydantic model awareness
"""

from __future__ import annotations

from typing import Any, Optional
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
class AsyncExpansionResult:
    """
    Result of an async attribute expansion operation.
    
    Attributes:
        success: Whether expansion completed successfully
        expanded_target: The target object with expanded attributes
        errors: List of (attribute_name, error) tuples for failed expansions
    """
    success: bool
    expanded_target: Any
    errors: list[tuple[str, Exception]]


class AsyncApiService:
    """
    Base async service class for all async congressgov.services API wrappers.
    
    Provides common async functionality for:
    - Client resolution with fallback logic
    - Attribute expansion by fetching additional data from API
    - Deep copying with Pydantic model awareness
    
    This class mirrors the sync ApiService but with async methods.
    
    Example:
        async_service = AsyncApiService()
        expanded = await async_service.expand(
            target=my_bill,
            client=api_client,
            mapping={"text": {fetch_text_async: TextModel}},
            parameters=["congress", "billType", "billNumber"]
        )
    """

    @staticmethod
    async def _resolve_client(target: Any, provided_client: Optional[Any] = None) -> Any:
        """
        Resolve the client parameter using fallback logic (async version).
        
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
            ClientNotFoundError: If no client can be resolved
            
        Example:
            >>> client = await AsyncApiService._resolve_client(my_bill, provided_client)
        """
        # Priority 1: Explicitly provided client
        if provided_client is not None:
            logger.debug("Using explicitly provided client")
            return provided_client
        
        # Priority 2: Client attribute on target
        if hasattr(target, 'client') and target.client is not None:
            logger.debug("Using client from target object")
            return target.client

        parent = getattr(target, '_parent_collection', None)
        if parent is not None and getattr(parent, 'client', None) is not None:
            logger.debug("Using client from parent collection")
            return parent.client
        
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
    def _deep_copy_target(target: Any) -> Any:
        """
        Create a deep copy of the target object (sync method, same as ApiService).
        
        Handles Pydantic models specially using model_copy().
        
        Args:
            target: Object to copy
            
        Returns:
            Deep copy of the target object
            
        Example:
            >>> copied_bill = AsyncApiService._deep_copy_target(original_bill)
        """
        # Check if target is a Pydantic model
        if hasattr(target, 'model_copy'):
            logger.debug("Creating deep copy using Pydantic model_copy()")
            return target.model_copy(deep=True)
        else:
            logger.debug("Creating deep copy using standard deepcopy()")
            return deepcopy(target)

    @staticmethod
    async def _expand_attribute(
        target: Any,
        attr_name: str,
        fetch_func: Any,
        model_class: Any,
        client: Any,
        parameters: dict[str, Any],
        **kwargs: Any,
    ) -> tuple[str, Any]:
        """
        Expand a single attribute by fetching data from API (async version).
        
        Args:
            target: Object to expand
            attr_name: Name of attribute to expand
            fetch_func: Async function to fetch the data
            model_class: Model class to parse the response
            client: API client
            parameters: Parameters to pass to fetch function
            
        Returns:
            Tuple of (attribute_name, expanded_data)
            
        Raises:
            Exception: If fetch or parsing fails
            
        Example:
            >>> name, data = await AsyncApiService._expand_attribute(
            ...     target=my_bill,
            ...     attr_name="actions",
            ...     fetch_func=fetch_actions_async,
            ...     model_class=ActionsModel,
            ...     client=api_client,
            ...     parameters={"congress": 118, "bill_type": "hr", "bill_number": 1}
            ... )
        """
        logger.debug(f"Expanding attribute: {attr_name}")
        
        # Call async fetch function
        resp = await fetch_func(client=client, **parameters, **kwargs)
        
        # Parse response
        api_env = ApiEnvelope.model_validate(json.loads(resp.content))
        expanded_data = model_class.model_validate(api_env.data)
        
        logger.debug(f"Successfully expanded attribute: {attr_name}")
        return attr_name, expanded_data

    @staticmethod
    async def expand(
        target: Any,
        client: Optional[Any] = None,
        mapping: Optional[dict[str, dict[Any, Any]]] = None,
        parameters: Optional[dict[str, Any]] = None,
        attributes: Optional[list[str]] = None,
        normalize_params: Optional[list[str]] = None,
        **kwargs: Any,
    ) -> AsyncExpansionResult:
        """
        Expand multiple attributes on a target object by fetching from API (async version).
        
        Args:
            target: Object to expand
            client: API client (will use target.client if not provided)
            mapping: Dict mapping attribute names to {fetch_func: model_class}
            parameters: Dict of parameters to extract from target
            attributes: List of specific attributes to expand (None = all)
            normalize_params: Parameter names to normalize to lowercase
            **kwargs: Additional keyword arguments passed to API functions
            
        Returns:
            AsyncExpansionResult with expanded target and any errors
            
        Example:
            >>> result = await AsyncApiService.expand(
            ...     target=my_bill,
            ...     client=api_client,
            ...     mapping={"actions": {fetch_actions_async: ActionsModel}},
            ...     parameters={"congress": "congress", "bill_type": "type"},
            ...     attributes=["actions"]
            ... )
            >>> expanded_bill = result.expanded_target
        """
        # Validate inputs
        if mapping is None:
            mapping = {}
        if parameters is None:
            parameters = {}
        
        # Resolve client
        from congressgov.services.exceptions import ClientNotFoundError

        try:
            resolved_client = await AsyncApiService._resolve_client(target, client)
        except ClientNotFoundError as e:
            logger.error(f"Client resolution failed: {e}")
            return AsyncExpansionResult(
                success=False,
                expanded_target=target,
                errors=[("_client_resolution", e)]
            )
        
        # Create deep copy
        expanded = AsyncApiService._deep_copy_target(target)
        
        # Determine which attributes to expand
        if attributes is None:
            attrs_to_expand = list(mapping.keys())
        else:
            attrs_to_expand = [attr for attr in attributes if attr in mapping]
        
        # Limit number of attributes
        if len(attrs_to_expand) > MAX_EXPANSION_ATTRIBUTES:
            logger.warning(
                f"Attempting to expand {len(attrs_to_expand)} attributes. "
                f"Limiting to {MAX_EXPANSION_ATTRIBUTES}."
            )
            attrs_to_expand = attrs_to_expand[:MAX_EXPANSION_ATTRIBUTES]
        
        try:
            extracted_params = extract_parameters_from_target(
                target,
                parameters,
                normalize_params=normalize_params,
            )
        except ValueError as e:
            logger.error(f"Parameter extraction failed: {e}")
            return AsyncExpansionResult(
                success=False,
                expanded_target=expanded,
                errors=[("_parameters", e)],
            )

        # Expand attributes concurrently
        import asyncio
        errors = []
        tasks = []
        
        for attr_name in attrs_to_expand:
            fetch_mapping = mapping[attr_name]
            fetch_func = list(fetch_mapping.keys())[0]
            model_class = fetch_mapping[fetch_func]
            
            task = AsyncApiService._expand_attribute(
                target=expanded,
                attr_name=attr_name,
                fetch_func=fetch_func,
                model_class=model_class,
                client=resolved_client,
                parameters=extracted_params,
                **kwargs,
            )
            tasks.append((attr_name, task))
        
        # Wait for all tasks to complete
        results = await asyncio.gather(
            *[task for _, task in tasks],
            return_exceptions=True
        )
        
        # Process results
        for (attr_name, _), result in zip(tasks, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to expand attribute '{attr_name}': {result}")
                errors.append((attr_name, result))
            else:
                # Set expanded attribute
                expanded_attr_name, expanded_data = result
                setattr(expanded, expanded_attr_name, expanded_data)
        
        # Attach client to expanded object
        if hasattr(expanded, 'client'):
            expanded.client = resolved_client
        
        success = len(errors) == 0
        return AsyncExpansionResult(
            success=success,
            expanded_target=expanded,
            errors=errors
        )


