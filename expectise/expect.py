# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import TYPE_CHECKING

from .diff import Diff
from .exceptions import EnvironmentError
from .exceptions import ExpectationError

if TYPE_CHECKING:
    # Prevent circular dependency
    from .mocks import Mock


class Expect(object):
    """
    Mocking function calls for unit tests purposes, refer to the README for more details and examples.
    """

    # Dict of classes with at least one method mocked, shared between Expect instances: {'class_name': class}
    class_h = {}
    # Dict of mocked methods, with potential arguments and outputs, shared between Expect instances):
    # {
    #   ('class_name', 'method_name'):
    #     {
    #       'method': callable_object,                      --> Method to decorate (original method)
    #       'expected': int,                                --> Expected number of calls to the method
    #       'performed': int,                               --> Performed number of calls to the method
    #       'decorators': [callable_object]                 --> list of decorators to apply to the original method
    #       'with_args': [((object), {string: object})],    --> list of (args, kwargs) the method should be called with
    #       'return': [object],                             --> list of outputs the decorated method should return
    #     }
    # }
    method_h = {}

    def __init__(self, class_name: str) -> None:
        if class_name not in Expect.class_h:
            raise EnvironmentError(
                f"""
                No method of class `{class_name}` is mocked, so this instantiation is not allowed.
                Check that the right environment variable is set, and that the right methods from `{class_name}`
                are decorated with `@mock_if` decorators or standalone `mock` statements.
                """
            )
        self.klass = Expect.class_h[class_name]
        self.method_name = None
        self.method = None
        self.is_classmethod = False
        self.is_staticmethod = False
        self.is_property = False
        # The order of decorators matters!
        self.decorator_names = ["raise", "return", "with_args", "classmethod", "staticmethod", "property"]
        self.decorators = {decorator_name: None for decorator_name in self.decorator_names}

    def set_method(self, method):
        """Set the method attribute to capture the decorated method, once known thanks to a `to_receive` call."""
        self.method = method
        if isinstance(method, classmethod):
            self.decorators["classmethod"] = classmethod
            self.is_classmethod = True
        if isinstance(method, staticmethod):
            self.decorators["staticmethod"] = staticmethod
            self.is_staticmethod = True
        if isinstance(method, property):
            self.decorators["property"] = property
            self.is_property = True

    def get_decoration(self) -> Callable:
        """Get the right decoration of the original method, depending on the number of calls already performed."""
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] - 1
        return Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][call_idx]

    def override_method(self) -> Callable:
        """
        Return the appropriate override of the mocked method to be applied during tests, according to Expect statements.
        This override includes checks on whether the method is called, and the right number of times.
        """

        def func(*args, **kwargs):
            self.mark_received()
            decorated = self.get_decoration()
            if self.is_classmethod or self.is_staticmethod:
                decorated = decorated.__func__
            elif self.is_property:
                decorated = decorated.fget
            return decorated(*args, **kwargs)

        if self.is_staticmethod:
            return staticmethod(func)
        elif self.is_classmethod:
            return classmethod(func)
        elif self.is_property:
            return property(func)
        return func

    def decorate(self) -> Callable:
        """Iteratively apply active decorators to the target method."""
        method = self.method
        if self.is_classmethod or self.is_staticmethod:
            method = method.__func__
        elif self.is_property:
            method = method.fget

        for decorator_name in self.decorator_names:
            decorator = self.decorators[decorator_name]
            method = decorator(method) if decorator else method
        return method

    def mark_received(self) -> None:
        """
        Mark the decorated method as called once more, and raise an exception if it is called more times than expected.
        """
        Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] += 1
        perf = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"]
        exp = Expect.method_h[(self.klass.__name__, self.method_name)]["expected"]
        if perf > exp:
            raise ExpectationError(
                "{}.{} is expected to be called {} time(s) only.".format(self.klass.__name__, self.method_name, exp)
            )

    def to_receive(self, method_name: str) -> Expect:
        """Decorate the mocked method to check that it is called."""
        key = (self.klass.__name__, method_name)
        self.method_name = method_name
        self.set_method(Expect.method_h[key]["mock"].surrogate)
        if key not in Expect.method_h:
            raise EnvironmentError(
                f"""
                Method `{method_name}` from class `{self.klass.__name__}` is not mocked.
                Decorate it with @mock_if(your_env_variable_name, your_env_variable_value), or through
                standalone mock() statements to be able to mock its calls.
                """
            )
        else:
            Expect.method_h[key]["expected"] += 1
            Expect.method_h[key]["decorators"].append(None)
            Expect.method_h[key]["with_args"].append(None)
            Expect.method_h[key]["return"].append(None)

        # Setting up decoration
        Expect.method_h[key]["decorators"][-1] = self.decorate()
        setattr(self.klass, self.method_name, self.override_method())
        return self

    def assert_arguments(self, func_args: List[Any], func_kwargs: Dict[Any, Any]) -> None:
        """Asserting equality of method arguments."""
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] - 1
        args, kwargs = Expect.method_h[(self.klass.__name__, self.method_name)]["with_args"][call_idx]

        msg = f"`{self.method_name}` method of `{self.klass.__name__}` called with " + "unexpected {} arguments:\n\n"
        if args != func_args:
            raise ExpectationError(msg.format("positional") + Diff.print(args, func_args))
        if kwargs != func_kwargs:
            raise ExpectationError(msg.format("keyword") + Diff.print(kwargs, func_kwargs))

    def with_args_decorator(self, method: Callable) -> Callable:
        """Decorator to check passed argument."""

        def instance_func(obj, *func_args, **func_kwargs):
            self.assert_arguments(func_args, func_kwargs)
            return method(obj, *func_args, **func_kwargs)

        def static_func(*func_args, **func_kwargs):
            self.assert_arguments(func_args, func_kwargs)
            return method(*func_args, **func_kwargs)

        return static_func if self.is_staticmethod else instance_func

    def with_args(self, *args, **kwargs) -> Expect:
        """Decorating a method to check it is called with the desired arguments."""
        if self.method is None:
            raise ExpectationError("Expect error: calling .with_args() without prior call of to_receive()")
        self.decorators["with_args"] = self.with_args_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]["with_args"][-1] = (args, kwargs)
        Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][-1] = self.decorate()
        return self

    def get_output(self) -> Any:
        """Get the right output to return when .and_return() decoration is used."""
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] - 1
        return Expect.method_h[(self.klass.__name__, self.method_name)]["return"][call_idx]

    def return_decorator(self, method: Callable) -> Callable:
        """Decorator to modify objects returned."""

        def func(*func_args, **func_kwargs):
            return self.get_output()

        return func

    def and_return(self, output: Any) -> Expect:
        """Overwrite a method to output the object passed as argument."""
        if self.method is None:
            raise ExpectationError("Expect error: calling and_return() without prior call of to_receive()")
        self.decorators["return"] = self.return_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]["return"][-1] = output
        Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][-1] = self.decorate()
        return self

    def raise_decorator(self, method: Callable) -> Callable:
        """Decorator to raise errors."""

        def func(*func_args, **func_kwargs):
            raise self.get_output()

        return func

    def and_raise(self, error: Exception) -> Expect:
        """Overwrite a method to raise an error when called."""
        if self.method is None:
            raise ExpectationError("Expect error: calling and_raise() without prior call of to_receive()")
        self.decorators["raise"] = self.raise_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]["return"][-1] = error
        Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][-1] = self.decorate()
        return self

    @classmethod
    def set_up(cls, mock: Mock) -> None:
        """
        Set up the `Expect` context and replace the method being mocked with a surrogate function.
        This method is called at interpretation time when `@mock_if` decorators are being resolved, when explicitly
        performing mock(...) statements, and at the end of each unit test to start the next one with a clean context.
        """
        # When called from `mock_if` decorating statement, adding classes to the list of altered objects
        if mock.klass.__name__ not in cls.class_h:
            cls.class_h[mock.klass.__name__] = mock.klass

        # Initializing the Expect context
        cls.method_h[(mock.klass.__name__, mock.name)] = {
            "expected": 0,
            "performed": 0,
            "decorators": [],
            "with_args": [],
            "return": [],
            "mock": mock,
        }
        # Substituting original methods with surrogates that raise errors if not preceded by `Expect` statements
        setattr(mock.klass, mock.name, mock.surrogate)

    @classmethod
    def disable_mock(cls, class_name: str, method_name: str) -> None:
        """Disables a Mock."""
        if not (class_name, method_name) in cls.method_h:
            raise ValueError(
                """
                Method `{method_name}` from class `{class_name}` is not mocked, or does not exist.
                Calling disable_mock has no effect.
                """
            )

        cls.method_h[(class_name, method_name)]["mock"].disable()

    @classmethod
    def tear_down(cls) -> None:
        """Check for any method called less times than expected, and raise an AssertionError is any is found."""
        message = ""
        for (class_name, method_name), args in cls.method_h.items():
            remain = args["expected"] - args["performed"]
            if remain > 0:
                message += f"`{method_name}` from class `{class_name}` still expected to be called {remain} time(s).\n"
            # Resetting Expect parameters and original methods, keeping the reference to the Mock object
            cls.set_up(cls.method_h[(class_name, method_name)]["mock"])

        # If some calls are still expected, message is not empty, so asserting False with the appropriate message
        assert not message, message
