from importlib import import_module
from typing import Callable
from typing import Type

from expectise.models.decoration import Decoration


class Kallable:
    """
    Kallable to represent a function or class method.

    This class is used to keep track of the function's or class method's metadata before it is replaced by a mock:
    orginal name, owning class or module, decoration, etc.
    """

    def __init__(self, ref: Callable, klass: Type | None = None):
        self.ref = ref
        self.decoration = Decoration(ref, klass=klass)
        ref_function = self.decoration.strip(ref)
        self.name = ref_function.__name__
        self.qualname = ref_function.__qualname__
        self.is_bound_method = "." in self.qualname  # for direct mock() statements, we can't know the owning class
        self.module_name = ref_function.__module__
        self.module = import_module(self.module_name)
        self._klass = klass
        self.id = f"{self.module_name}.{self.qualname}"

    @property
    def klass(self):
        if self._klass:
            return self._klass
        if self.is_bound_method:
            return getattr(self.module, self.qualname.split(".")[0])
        return None

    @klass.setter
    def klass(self, value):
        self._klass = value

    @property
    def owner(self):
        """
        Get the owner of the function or method.
        * For a class method, it is the class itself. It may be passed in the constructor or inferred from the
        method's qualname.
        * For a standalone function, it is the module itself.
        """
        if self.klass:
            return self.klass

        return self.module
