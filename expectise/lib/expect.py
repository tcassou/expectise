from __future__ import annotations

from typing import Any
from typing import Callable

from .session import session
from expectise.exceptions import EnvironmentError


class Expect(object):
    """
    A class to describe the expected behavior of a function or method that is already marked as mocked.

    It can be used to:
    * describe the arguments that the function or method should be called with;
    * describe the output that the function or method should return;
    * describe the error that the function or method should raise.

    Example:
    ```python
    Expect(SomeAPI.get_something).to_receive("foo", "bar").and_return(False)
    Expect(SomeAPI.get_something).to_raise(ValueError("My error"))
    ```
    """

    def __init__(self, mock_ref: Callable) -> None:
        """Initialize an Expect instance with the function or method to be mocked."""
        marker = session.get_marker(mock_ref)
        if not marker.enabled:
            raise EnvironmentError(
                f"The marker for `{marker.kallable.id}` is not enabled, so this instantiation is not allowed. "
                "Check that the right environment variable are set."
            )

        self.kallable = marker.kallable
        self.mock.new()

    @property
    def mock(self):
        """Return the Mock object associated with the function or method."""
        return session.markers[self.kallable.id].mock

    def to_receive(self, *args, **kwargs) -> Expect:
        """Describe the arguments that the function or method should be called with."""
        self.mock.add_argument_check(args, kwargs)
        return self

    def to_return(self, output: Any) -> Expect:
        """Describe the output that the function or method should return."""
        self.mock.add_return_value(output)
        return self

    def and_return(self, output: Any) -> Expect:
        """Alias for `to_return`."""
        return self.to_return(output)

    def to_raise(self, error: Exception) -> Expect:
        """Describe the error that the function or method should raise."""
        self.mock.add_execution_errors(error)
        return self

    def and_raise(self, error: Exception) -> Expect:
        """Alias for `to_raise`."""
        return self.to_raise(error)
