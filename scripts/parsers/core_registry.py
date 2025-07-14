# cores/core_registry.py
from typing import Type, Iterable, Dict, Optional, Any

# Registry mapping kind_id to core class
CORE_REGISTRY: Dict[int, Type[Any]] = {}


def register_core(kind_ids: Iterable[int]):
    """
    Decorator to register a core element class for given kind_id(s).

    Usage:
        @register_core([1, 2, 3])
        class Beam(Edge):
            ...
    """

    def decorator(cls: Type[Any]) -> Type[Any]:
        for kid in kind_ids:
            CORE_REGISTRY[kid] = cls
        return cls

    return decorator


def unregister_core(kind_id: int) -> None:
    """
    Unregister a core class for a given kind_id.
    """
    CORE_REGISTRY.pop(kind_id, None)


def get_core_class(kind_id: int) -> Optional[Type[Any]]:
    """
    Retrieve the registered core class for a given kind_id.
    Falls back to None if not registered.
    """
    return CORE_REGISTRY.get(kind_id)


def list_core_classes() -> Dict[int, Type[Any]]:
    """
    Return a copy of the current kind_id → core class registry.
    """
    return dict(CORE_REGISTRY)
