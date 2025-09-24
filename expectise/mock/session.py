from typing import Optional

from .marker import Marker
from expectise.exceptions import EnvironmentError
from expectise.models import Lifespan
from expectise.models.decoration import Decoration
from expectise.models.method import Method
from expectise.models.trigger import Trigger


class Session:
    def __init__(self):
        self.markers = {}

    def mark_method(self, method: Method, trigger: Trigger, lifespan: Lifespan) -> Marker:
        """Mark a method as mocked, without enabling the marker yet."""
        marker = Marker(method, trigger=trigger, lifespan=lifespan)
        self.markers[method.id] = marker
        return marker

    def get_marker(self, mock_ref: str) -> Marker:
        """
        Get a marker, given a mock reference.
        Once a method is marked as mocked and the marker is enabled, accessing it will return the mock object and not
        the original method anymore.
        The mock object keeps track of the original method identifier, which creates the connection between the marker
        and the mock object.
        """
        decoration = Decoration(mock_ref)
        mock_function = decoration.strip(mock_ref)
        if not hasattr(mock_function, "_original_id"):
            method = Method(mock_ref)
            raise EnvironmentError(
                f"Method `{method.id}` is not marked as mocked, so this instantiation is not allowed. "
                "Check that the right environment variable are set, and that the method is marked as mocked "
                "with the `@mock_if` decorator, or through standalone `mock` statements."
            )

        return self.markers[mock_function._original_id]

    def drop_temporary_markers(self):
        """Drop all temporary markers and their related mocks from the session."""
        temporary_markers = [m_id for m_id, marker in self.markers.items() if marker.lifespan == Lifespan.TEMPORARY]
        for marker_id in temporary_markers:
            self.markers.pop(marker_id)

    def tear_down(self, execution_error: Optional[Exception] = None):
        """"""
        message = ""
        for method_id, marker in self.markers.items():

            if (gap := marker.mock.expected - marker.mock.performed) > 0:
                message += f"`{method_id}` still expected to be called {gap} time(s).\n"

            if marker.lifespan == Lifespan.PERMANENT:
                marker.reset()  # Permanent markers do not go away during tear_down, only their mocks are reset
            elif marker.lifespan == Lifespan.TEMPORARY:
                marker.disable()  # Temporary markers are fully disabled during tear_down, and removed from the session

        # Fully removing all references to temporary markers
        self.drop_temporary_markers()

        # In case an exception was raised during the test, raising it again
        if execution_error:
            raise execution_error

        # If some calls are still expected, message is not empty, so asserting False with the appropriate message
        assert not message, message


session = Session()
