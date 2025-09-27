from .mock import Mock
from expectise.exceptions import EnvironmentError
from expectise.models import Lifespan
from expectise.models.kallable import Kallable
from expectise.models.trigger import Trigger


class Marker:
    """
    Marker to indicate that a function or method is mocked, and block any calls to the original function or method.

    There are 2 different types of markers:
    * Permanent markers: created using the `mock_if` decorator, they are active only when the right
    environment variable is set. Permanent markers are not removed between individual tests.
    * Temporary markers: created using the `mock` function, they are active only for the duration of the test.
    Temporary markers are removed between individual tests.

    Once a marker is set on a function or method, its behavior can be described using `Expect` statements.
    """

    def __init__(self, kallable: Kallable, trigger: Trigger, lifespan: Lifespan) -> None:
        self.kallable = kallable
        self.mock = Mock(kallable)
        self.trigger = trigger
        self.lifespan = lifespan
        self.enabled = False  # toggled everytime the marker is enabled or disabled
        self.disabled = False  # toggled when a mock is explicitly disabled

    @property
    def placeholder(self):
        """
        Return a placeholder function that will replace the mocked function or method under when the trigger is met.
        """

        def func(*args, **kwargs):
            raise EnvironmentError(
                f"Callable `{self.kallable.id}` is marked as mocked, "
                "and will raise errors if called without using an `Expect` statement to define its mocked behavior."
            )

        func._original_id = self.kallable.id
        return self.kallable.decoration.add(func)

    def set_up(self):
        """
        Replace the mocked function or method with its placeholder, if the right conditions are met,
        in order to forbid calls to the original function or method.
        """
        if self.trigger.is_met():
            setattr(self.kallable.owner, self.kallable.name, self.placeholder)
            self.enabled = True
        else:
            self.disable()

    def disable(self, mark_disabled: bool = False):
        """Restore the original function or method and remove any mocking logic."""
        setattr(self.kallable.owner, self.kallable.name, self.kallable.ref)
        self.enabled = False
        self.disabled = mark_disabled

    def reset(self):
        """Reset the marker and its mock object."""
        self.mock.reset()
        self.set_up()
        self.disabled = False
