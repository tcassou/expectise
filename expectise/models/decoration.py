from typing import Callable


class Decoration:
    def __init__(self, ref: Callable):
        self.is_classmethod = isinstance(ref, classmethod)
        self.is_staticmethod = isinstance(ref, staticmethod)
        self.is_property = isinstance(ref, property)

    def strip(self, ref: Callable) -> Callable:
        """Strip the decorator of the callable."""
        if self.is_classmethod or self.is_staticmethod:
            return ref.__func__
        if self.is_property:
            return ref.fget
        return ref

    def add(self, ref: Callable) -> Callable:
        """Add decoration to the callable."""
        if self.is_classmethod:
            return classmethod(ref)
        if self.is_staticmethod:
            return staticmethod(ref)
        if self.is_property:
            return property(ref)
        return ref
