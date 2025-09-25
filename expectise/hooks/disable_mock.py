from typing import Callable

from expectise.lib.session import session


def disable_mock(mock_ref: Callable) -> None:
    """
    Disable a mock marker, given the mocked method reference.
    This is useful for disabling a permanent mock marker that was created with the `mock_if` decorator.
    Once the marker is disabled, the method can be called and tested without any alteration of its behavior.
    """
    marker = session.get_marker(mock_ref)
    marker.disable(mark_disabled=True)
