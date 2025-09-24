from expectise.exceptions import EnvironmentError
from expectise.mock.mock import Mock
from expectise.models import Lifespan
from expectise.models.method import Method
from expectise.models.trigger import Trigger


class Marker:
    """
    Marker to indicate that a function or method is mocked, and block any calls to the original method.

    There are 2 different types of markers:
    * Permanent markers: created using the `mock_if` decorator, they are active only when the right
    environment variable is set. Permanent markers are not removed between individual tests.
    * Temporary markers: created using the `mock` function, they are active only for the duration of the test.
    Temporary markers are removed between individual tests.

    Once a marker is set on a function or method, its behavior can be described using `Expect` statements.
    """

    def __init__(self, method: Method, trigger: Trigger, lifespan: Lifespan) -> None:
        self.method = method
        self.mock = Mock(method)
        self.trigger = trigger
        self.lifespan = lifespan

    @property
    def placeholder(self):
        """Return a placeholder function that will replace the mocked method under the right environment context."""

        def func(*args, **kwargs):
            raise EnvironmentError(
                f"Method `{self.method.id}` is marked as mocked, "
                "and will raise errors if called without using an `Expect` statement to define its mocked behavior."
            )

        func._original_id = self.method.id
        return self.method.decoration.add(func)

    def enable(self):
        """Replace the mocked method with its placeholder in order to forbid calls to the original method."""
        setattr(self.method.owner, self.method.name, self.placeholder)

    def disable(self):
        """Restore the original method and remove any mocking logic."""
        setattr(self.method.owner, self.method.name, self.method.ref)

    def reset(self):
        """Reset the marker and its mock."""
        self.mock.reset()
        self.enable()
