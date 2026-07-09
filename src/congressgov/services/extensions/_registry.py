"""
`@register_method` attaches a plain function to a model class as a method,
which is how query/filter helpers get onto `Members`, `Bills`, etc. without
those classes importing anything beyond Pydantic. Registrations are tracked
in `_REGISTRY` for introspection (see `get_registered_methods`, `print_registry`).
"""
from __future__ import annotations
from typing import Callable, TypeVar, Type

# Type variable for generic class
T = TypeVar('T')

# Track all registered methods for debugging/introspection
_REGISTRY: dict[str, dict[str, Callable]] = {}


def register_method(target_class: Type[T], method_name: str | None = None) -> Callable:
    """Decorator that attaches the decorated function to `target_class` as a method.

    Usage::

        @register_method(Members)
        def filter(self, **kwargs):
            return self.query().filter(**kwargs)
    """
    def decorator(func: Callable) -> Callable:
        name = method_name or func.__name__
        class_name = target_class.__name__

        setattr(target_class, name, func)

        if class_name not in _REGISTRY:
            _REGISTRY[class_name] = {}
        _REGISTRY[class_name][name] = func

        return func

    return decorator


def get_registered_methods(class_name: str) -> dict[str, Callable]:
    """Return the registered {method_name: function} map for a class, e.g. "Members"."""
    return _REGISTRY.get(class_name, {})


def get_registered_models() -> list[str]:
    """Return the names of all classes with at least one registered method."""
    return list(_REGISTRY.keys())


def print_registry() -> None:
    """Print every registered class and its methods; a debugging convenience only."""
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

