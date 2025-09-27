from typing import Callable

from .marker import Marker
from expectise.exceptions import EnvironmentError
from expectise.exceptions import ExpectationError
from expectise.models import Lifespan
from expectise.models.decoration import Decoration
from expectise.models.kallable import Kallable
from expectise.models.trigger import Trigger


class Session:
    """
    Session to manage the mocked functions and methods.

    The session is responsible for:
    * marking functions and methods as mocked,
    * storing the mocked functions and methods,
    * tearing down the session and resetting the mocked functions and methods after each test.
    """

    def __init__(self):
        """Initialize the session with an empty dictionary of markers."""
        self.markers = {}

    def mark_method(self, kallable: Kallable, trigger: Trigger, lifespan: Lifespan) -> Marker:
        """Mark a function or method as mocked, without enabling the marker yet."""
        marker = Marker(kallable, trigger=trigger, lifespan=lifespan)
        self.markers[kallable.id] = marker
        return marker

    def get_marker(self, mock_or_ref: Callable) -> Marker:
        """
        Get a marker, given an inpput callable that may be a mock already set, or a function to be mocked on the fly.

        Once a class method is marked as mocked and the marker is enabled, accessing it will return
        the mock object and not the original method anymore.
        For a function marked as mocked, while the marker is created early (at interpretation time with mock_if,
        or when calling `mock()`), the marker needs to be enabled on the fly when `Expect` statements are used.

        The mock object keeps track of the original callable identifier, which creates the connection between the marker
        and the mock object.
        """
        decoration = Decoration(mock_or_ref)
        function = decoration.strip(mock_or_ref)

        if hasattr(function, "_original_id"):
            # we're given a mock, so we know the marker is set and enabled
            kallable_id = function._original_id
        else:
            # we're given a function or method, so we need to check if the marker is set and enabled
            # this is a valid case when using `mock()` statements for standalone functions
            kallable_id = Kallable(mock_or_ref).id
            if kallable_id not in self.markers:
                raise EnvironmentError(
                    f"Callable `{kallable_id}` is not marked as mocked, so this instantiation is not allowed. "
                    "Check that the right environment variable are set, and that the method is marked as mocked "
                    "with the `@mock_if` decorator, or through standalone `mock` statements."
                )

        marker = self.markers[kallable_id]
        if marker.kallable.klass is None and not marker.disabled:
            # for standalone functions without explicitly disabled markers, the marker is enabled on the fly
            marker.set_up()

        return marker

    def tear_down(self, exception: Exception = None):
        """
        Tear down the session and reset the mocked functions and methods.
        * Permanent markers are not removed during tear down, only their mocks are reset.
        * Temporary markers are fully disabled during tear down, and removed from the session.
        * If some function or method calls are still expected, an error is raised to indicate the missing expectations.
        """
        expected_calls = []
        temporary_markers = []
        for kallable_id, marker in self.markers.items():

            if (gap := marker.mock.expected - marker.mock.performed) > 0:
                expected_calls.append(f"`{kallable_id}` still expected to be called {gap} time(s).")

            if marker.lifespan == Lifespan.PERMANENT:
                marker.reset()  # Permanent markers do not go away during tear_down, only their mocks are reset
            elif marker.lifespan == Lifespan.TEMPORARY:
                marker.disable()  # Temporary markers are fully disabled during tear_down, and removed from the session
                temporary_markers.append(kallable_id)

        # Fully removing all references to temporary markers
        for kallable_id in temporary_markers:
            self.markers.pop(kallable_id)

        if exception:
            raise exception

        # If some calls are still expected, message is not empty, so asserting False with the appropriate message
        if expected_calls:
            raise ExpectationError("\n".join(expected_calls))


# Singleton instance of the session
session = Session()
