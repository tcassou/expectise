from typing import Callable
from typing import Type


class Decoration:
    """
    Decoration to manage the base decoration of a function or method: classmethod, staticmethod, property.

    It can be used to:
    * strip the decoration of a function or method;
    * add back its decoration to a function or method.
    """

    def __init__(self, ref: Callable, klass: Type | None = None):
        self.is_property = isinstance(ref, property)
        self.is_classmethod = isinstance(ref, classmethod)
        self.is_staticmethod = isinstance(ref, staticmethod)

    def strip(self, ref: Callable) -> Callable:
        """Strip the decorator of the callable."""
        if self.is_property:
            return ref.fget
        if self.is_classmethod or self.is_staticmethod:
            return ref.__func__
        return ref

    def add(self, ref: Callable) -> Callable:
        """Add decoration to the callable."""
        if self.is_property:
            return property(ref)
        if self.is_classmethod:
            return classmethod(ref)
        if self.is_staticmethod:
            return staticmethod(ref)
        return ref
