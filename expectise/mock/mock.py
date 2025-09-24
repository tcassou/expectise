from typing import Any
from typing import Callable
from typing import Dict
from typing import List

from expectise.exceptions import EnvironmentError
from expectise.exceptions import ExpectationError
from expectise.models.method import Method
from expectise.utils.diff import Diff


class MockInstance:
    def __init__(self):
        self.surrogate = None
        self.call_arguments = None
        self.return_value = None
        self.execution_error = None


class Mock:
    def __init__(self, method: Method):
        self.method = method
        self.reset()

    def reset(self) -> None:
        self.expected = 0
        self.performed = 0
        self.surrogates = []
        self.call_arguments = []
        self.return_values = []
        self.execution_errors = []

    def new(self):
        """"""
        self.expected += 1
        self.surrogates.append(None)
        self.call_arguments.append(None)
        self.return_values.append(None)
        self.execution_errors.append(None)
        setattr(self.method.owner, self.method.name, self.override)

    def add_argument_check(self, args: List[Any], kwargs: Dict[Any, Any]) -> None:
        """Adding an argument check to the mock."""
        self.call_arguments[-1] = (args, kwargs)

    def mark_call_received(self) -> None:
        """Mark the mocked method as called, and raise an exception if it is called more times than expected."""
        self.performed += 1
        if self.performed > self.expected:
            raise ExpectationError(f"{self.method.id} is expected to be called {self.expected} time(s) only.")

    def add_return_value(self, value: Any) -> None:
        """Adding a return value to the mock, and maintain call arguments checks if any."""
        self.return_values[-1] = value
        surrogate = self._return
        if self.call_arguments[-1] is not None:
            surrogate = self._check_arguments(surrogate)
        self.surrogates[-1] = self.method.decoration.add(surrogate)

    def add_execution_errors(self, value: Any) -> None:
        """Adding an execution error to the mock, and maintain call arguments checks if any."""
        self.execution_errors[-1] = value
        surrogate = self._raise
        if self.call_arguments[-1] is not None:
            surrogate = self._check_arguments(surrogate)
        self.surrogates[-1] = self.method.decoration.add(surrogate)

    @property
    def override(self) -> Callable:
        """
        Return the appropriate override of the mocked method to be applied during tests, according to Expect statements.
        This override includes checks on whether the method is called, and the right number of times.
        """

        def func(*args, **kwargs):
            self.mark_call_received()
            if self.surrogates[self.performed - 1] is None:
                raise EnvironmentError(
                    f"Incomplete `Expect` statement for method `{self.method.id}`. "
                    "Make sure the mock is properly set up by defining the expected return value or execution error."
                )

            surrogate = self.method.decoration.strip(self.surrogates[self.performed - 1])
            return surrogate(*args, **kwargs)

        func._original_id = self.method.id
        return self.method.decoration.add(func)

    def assert_arguments(self, func_args: List[Any], func_kwargs: Dict[Any, Any]) -> None:
        """Asserting equality of method arguments."""
        args, kwargs = self.call_arguments[self.performed - 1]
        msg = f"`{self.method.id}` called with " + "unexpected {} arguments:\n\n"
        if args != func_args:
            raise ExpectationError(msg.format("positional") + Diff.print(args, func_args))
        if kwargs != func_kwargs:
            raise ExpectationError(msg.format("keyword") + Diff.print(kwargs, func_kwargs))

    def _check_arguments(self, method: Callable) -> Callable:
        """Decorator to check passed argument."""

        def instance_func(obj, *func_args, **func_kwargs):
            self.assert_arguments(func_args, func_kwargs)
            return method(obj, *func_args, **func_kwargs)

        def static_func(*func_args, **func_kwargs):
            self.assert_arguments(func_args, func_kwargs)
            return method(*func_args, **func_kwargs)

        return static_func if self.method.decoration.is_staticmethod else instance_func

    def _return(self, *args, **kwargs) -> Any:
        """Simulate an object being returned."""
        return self.return_values[self.performed - 1]

    def _raise(self, *args, **kwargs) -> None:
        """Simulate an error being raised."""
        raise self.execution_errors[self.performed - 1]
