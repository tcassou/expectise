from __future__ import annotations

from typing import Any
from typing import Callable

from expectise.mock.session import session


class Expect(object):

    def __init__(self, mock_ref: Callable) -> None:
        """Initialize an Expect instance with the class to be mocked."""
        self.method = session.get_marker(mock_ref).method
        self.mock.new()

    @property
    def mock(self):
        """Return the Mock object associated with the method."""
        return session.markers[self.method.id].mock

    def to_receive(self, *args, **kwargs) -> Expect:
        """Decorating a method to check it is called with the desired arguments."""
        self.mock.add_argument_check(args, kwargs)
        return self

    def to_return(self, output: Any) -> Expect:
        """Overwrite a method to output the object passed as argument."""
        self.mock.add_return_value(output)
        return self

    def and_return(self, output: Any) -> Expect:
        return self.to_return(output)

    def to_raise(self, error: Exception) -> Expect:
        """Overwrite a method to raise an error when called."""
        self.mock.add_execution_errors(error)
        return self

    def and_raise(self, error: Exception) -> Expect:
        return self.to_raise(error)
