from importlib import import_module
from typing import Callable
from typing import Type

from expectise.models.decoration import Decoration


class Method:
    def __init__(self, ref: Callable, owner: Type | None = None):
        self.ref = ref
        self.decoration = Decoration(ref)
        ref_function = self.decoration.strip(ref)
        self.name = ref_function.__name__
        self.qualname = ref_function.__qualname__
        self.module_name = ref_function.__module__
        self.module = import_module(self.module_name)
        self.owner_name = ref_function.__qualname__.split(".")[0] if "." in ref_function.__qualname__ else None
        self.owner = owner if owner else getattr(self.module, self.owner_name)
        self.id = f"{self.module_name}.{self.qualname}"
