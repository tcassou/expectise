from typing import Any
from typing import Tuple

from expectise.exceptions import EnvironmentError


class MockInstance:
    """
    A mocked function or method may be called several times during a test, with varying arguments and return values.
    This class is used to store the configuration of a single call to the mocked method.
    """

    def __init__(self):
        self.has_argument_check = False
        self._call_arguments = None
        self.has_return_value = False
        self._return_value = None
        self.has_execution_error = False
        self._execution_error = None

    def assert_incomplete(self) -> None:
        """
        Check that the mock instance configuration is not complete, and raise an error if it is.
        A mock instance is considered complete when it has either a return value or an execution error.
        """
        if self.has_return_value:
            raise EnvironmentError("Return value already set for this mock instance.")
        if self.has_execution_error:
            raise EnvironmentError("Execution error already set for this mock instance.")

    @property
    def call_arguments(self) -> Tuple[list[Any], dict[Any, Any]]:
        return self._call_arguments

    @call_arguments.setter
    def call_arguments(self, value: Tuple[list[Any], dict[Any, Any]]) -> None:
        if self.has_argument_check:
            raise EnvironmentError("Arguments check already set for this mock instance.")
        self._call_arguments = value
        self.has_argument_check = True

    @property
    def return_value(self) -> Any:
        return self._return_value

    @return_value.setter
    def return_value(self, value: Any) -> None:
        self.assert_incomplete()
        self._return_value = value
        self.has_return_value = True

    @property
    def execution_error(self) -> Exception:
        return self._execution_error

    @execution_error.setter
    def execution_error(self, value: Exception) -> None:
        self.assert_incomplete()
        self._execution_error = value
        self.has_execution_error = True
