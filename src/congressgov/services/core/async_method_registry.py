"""
Async Method Registry for dynamically adding async methods to model classes.

This module provides the @register_async_method decorator which allows
dynamically adding async methods to Pydantic model classes at runtime.

This mirrors the sync @register_method decorator but for async methods.
"""

from typing import Callable
import logging

logger = logging.getLogger(__name__)


def register_async_method(target_class: type) -> Callable:
    """
    Decorator to register an async method on a target class.
    
    This allows dynamically adding async methods to model classes without
    modifying the model class definition directly. The method is added
    as a bound method to the class.
    
    Args:
        target_class: The class to add the method to
        
    Returns:
        Decorator function that registers the method
        
    Example:
        >>> @register_async_method(Bill)
        >>> async def get_actions_async(self, client=None):
        ...     '''Get actions for this bill asynchronously.'''
        ...     # Implementation
        ...     pass
        
        >>> # Now Bill instances have get_actions_async method
        >>> bill = Bill(...)
        >>> actions = await bill.get_actions_async()
    
    Note:
        - The decorated function's first parameter must be 'self'
        - The method will be available on all instances of target_class
        - Type hints are preserved for IDE support
    """
    def decorator(func: Callable) -> Callable:
        method_name = func.__name__
        
        # Add method to class
        setattr(target_class, method_name, func)
        
        logger.debug(
            f"Registered async method '{method_name}' on class '{target_class.__name__}'"
        )
        
        return func
    
    return decorator


def unregister_async_method(target_class: type, method_name: str) -> bool:
    """
    Unregister an async method from a target class.
    
    Args:
        target_class: The class to remove the method from
        method_name: Name of the method to remove
        
    Returns:
        True if method was removed, False if it didn't exist
        
    Example:
        >>> unregister_async_method(Bill, 'get_actions_async')
        True
    """
    if hasattr(target_class, method_name):
        delattr(target_class, method_name)
        logger.debug(
            f"Unregistered async method '{method_name}' from class '{target_class.__name__}'"
        )
        return True
    else:
        logger.warning(
            f"Attempted to unregister non-existent async method '{method_name}' "
            f"from class '{target_class.__name__}'"
        )
        return False


def get_async_methods(target_class: type) -> list[str]:
    """
    Get list of all async methods registered on a class.
    
    Args:
        target_class: The class to inspect
        
    Returns:
        List of async method names
        
    Example:
        >>> async_methods = get_async_methods(Bill)
        >>> print(async_methods)
        ['get_actions_async', 'get_amendments_async', 'expand_async']
    """
    import inspect
    
    async_methods = []
    for name, method in inspect.getmembers(target_class, predicate=inspect.iscoroutinefunction):
        if not name.startswith('_'):  # Exclude private methods
            async_methods.append(name)
    
    return async_methods


