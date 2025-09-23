from expectise.exceptions import EnvironmentError
from expectise.models import Lifespan
from expectise.models.method import Method
from expectise.models.trigger import Trigger


class Marker:
    """Represent a mocked method and its behaviour depending on the environment context."""

    def __init__(self, method: Method, trigger: Trigger, lifespan: Lifespan) -> None:
        self.method = method
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
