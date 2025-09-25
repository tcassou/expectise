from typing import Any
from typing import Callable

from .mock_instance import MockInstance
from expectise.exceptions import EnvironmentError
from expectise.exceptions import ExpectationError
from expectise.models.kallable import Kallable
from expectise.utils.diff import Diff


class Mock:
    """
    Mock object to store the configuration of a mocked function or method.

    Once a function or method is marked as mocked, it is replaced by a placeholder that raises an error if called
    without using an `Expect` statement to define its mocked behavior.

    This mock object is used to store the configuration of a mocked function or method, and to override the mocked
    method with the appropriate surrogate that will perform the checks on the calls and return the appropriate values.

    A single Mock object may hold multiple mock instances, each corresponding to a single call
    to the mocked function or method.
    """

    def __init__(self, kallable: Kallable):
        self.kallable = kallable
        self.reset()

    def reset(self) -> None:
        """Reset the mock: remove all instances and expected calls."""
        self.performed = 0
        self.instances = []

    def new(self):
        """Create a new mock instance, and override the mocked function or method with the appropriate surrogate."""
        self.instances.append(MockInstance())
        setattr(self.kallable.owner, self.kallable.name, self.override)

    @property
    def expected(self) -> int:
        """Get the number of expected calls."""
        return len(self.instances)

    @property
    def last_instance(self) -> MockInstance:
        """Get the last mock instance created."""
        return self.instances[-1]

    @property
    def current_instance(self) -> MockInstance:
        """Get the current mock instance, taking into account the number of calls already performed."""
        return self.instances[self.performed - 1]

    def add_argument_check(self, args: list[Any], kwargs: dict[Any, Any]) -> None:
        """Add an argument check to the mock."""
        self.last_instance.call_arguments = (args, kwargs)

    def add_return_value(self, value: Any) -> None:
        """Add a return value to the mock."""
        self.last_instance.return_value = value

    def add_execution_errors(self, value: Any) -> None:
        """Add an execution error to the mock."""
        self.last_instance.execution_error = value

    def mark_call_received(self) -> None:
        """
        Mark the mocked function or method as called, and raise an exception if it is being called more times
        than expected.
        """
        self.performed += 1
        if self.performed > self.expected:
            raise ExpectationError(f"{self.kallable.id} is expected to be called {self.expected} time(s) only.")

    def assert_arguments(self, func_args: list[Any], func_kwargs: dict[Any, Any]) -> None:
        """Assert equality of function or method call arguments with the expected arguments."""
        args, kwargs = self.current_instance.call_arguments
        args_start_index = 1 if (self.kallable.is_bound_method and not self.kallable.decoration.is_staticmethod) else 0
        msg = f"`{self.kallable.id}` called with " + "unexpected {} arguments:\n\n"
        if args != func_args[args_start_index:]:
            raise ExpectationError(msg.format("positional") + Diff.print(args, func_args[args_start_index]))
        if kwargs != func_kwargs:
            raise ExpectationError(msg.format("keyword") + Diff.print(kwargs, func_kwargs))

    @property
    def override(self) -> Callable:
        """
        Return the appropriate override of the mocked function or method to be applied during tests,
        according to Expect statements. This override includes:
        * checks on whether the function or method is called, and the right number of times,
        * checks on whether the function or method is called with the expected arguments,
        * the appropriate return value or execution error as configured by the `Expect` statements.
        """

        def func(*args, **kwargs):
            self.mark_call_received()
            mock_instance = self.current_instance
            if not mock_instance.has_return_value and not mock_instance.has_execution_error:
                raise EnvironmentError(
                    f"Incomplete `Expect` statement for callable `{self.kallable.id}`. "
                    "Make sure the mock is properly set up by defining the expected return value or execution error."
                )
            if mock_instance.has_argument_check:
                self.assert_arguments(args, kwargs)
            if mock_instance.has_return_value:
                return mock_instance.return_value
            if mock_instance.has_execution_error:
                raise mock_instance.execution_error

        func._original_id = self.kallable.id
        return self.kallable.decoration.add(func)
