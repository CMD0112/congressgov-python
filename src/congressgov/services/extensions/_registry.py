"""
Method Registration Registry

Provides decorators and utilities for dynamically registering methods
on model classes without modifying the model files.

This registry system:
- Avoids circular imports
- Keeps models clean (pure Pydantic)
- Centralizes extension logic
- Supports multiple target classes
- Tracks registered methods for debugging
"""
from __future__ import annotations
from typing import Callable, TypeVar, Type

# Type variable for generic class
T = TypeVar('T')

# Track all registered methods for debugging/introspection
_REGISTRY: dict[str, dict[str, Callable]] = {}


def register_method(target_class: Type[T], method_name: str | None = None) -> Callable:
    """
    Decorator to register a function as a method on a target class.
    
    Args:
        target_class: The class to add the method to
        method_name: Optional custom method name (default: use function name)
    
    Usage:
        @register_method(Members)
        def filter(self, **kwargs):
            return self.query().filter(**kwargs)
        
        @register_method(Members, "custom_name")
        def my_function(self):
            return "custom"
    
    The function becomes a method on the target class.
    """
    def decorator(func: Callable) -> Callable:
        # Use provided method name or function name
        name = method_name or func.__name__
        
        # Get class name for registry
        class_name = target_class.__name__
        
        # Import lazily to avoid circular imports
        # The target_class is passed directly, so no import needed
        
        # Register the method on the class
        setattr(target_class, name, func)
        
        # Track in registry for introspection
        if class_name not in _REGISTRY:
            _REGISTRY[class_name] = {}
        _REGISTRY[class_name][name] = func
        
        return func
    
    return decorator


def get_registered_methods(class_name: str) -> dict[str, Callable]:
    """
    Get all registered methods for a class.
    
    Args:
        class_name: Name of the class (e.g., "Members")
    
    Returns:
        Dictionary mapping method names to functions
    
    Example:
        methods = get_registered_methods("Members")
        print(list(methods.keys()))  # ['filter', 'by_state', ...]
    """
    return _REGISTRY.get(class_name, {})


def get_registered_models() -> list[str]:
    """
    Get list of all model classes that have registered methods.
    
    Returns:
        List of class names
    
    Example:
        models = get_registered_models()
        print(models)  # ['Members', 'Bills', 'Committees']
    """
    return list(_REGISTRY.keys())


def print_registry() -> None:
    """
    Print a formatted view of the method registry.
    
    NOTE: This is a debug/development utility function.
    NOTE: Intended for interactive debugging and extension development.
    
    Useful for:
    - Verifying which methods are registered on which models
    - Debugging extension registration issues
    - Generating documentation of available extension methods
    """
    print("=" * 60)
    print("REGISTERED METHOD EXTENSIONS")
    print("=" * 60)
    
    if not _REGISTRY:
        print("No methods registered yet.")
        return
    
    for class_name, methods in sorted(_REGISTRY.items()):
        print(f"\n{class_name}:")
        for method_name in sorted(methods.keys()):
            print(f"  - {method_name}()")
    
    print("\n" + "=" * 60)

