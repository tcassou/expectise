from typing import Callable

from expectise.lib.session import session
from expectise.models import Lifespan
from expectise.models.kallable import Kallable
from expectise.models.trigger import AlwaysTrigger


def mock(ref: Callable) -> None:
    """
    Mark a function or class method as temporarily mocked.
    * Once marked, a function or method cannot be called without using an `Expect` statement to define its behavior.
    * A temporary marker is automatically removed when the Expectise session is torn down.
    """
    kallable = Kallable(ref)  # without any dynamic imports, no easy way to know the owning class here, if applicable
    marker = session.mark_method(kallable, trigger=AlwaysTrigger(), lifespan=Lifespan.TEMPORARY)
    marker.set_up()
