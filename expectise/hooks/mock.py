from typing import Callable

from expectise.mock.session import session
from expectise.models import Lifespan
from expectise.models.method import Method
from expectise.models.trigger import AlwaysTrigger


def mock(ref: Callable) -> None:
    """
    Mark a method as temporarily mocked.
    * Once marked, a method cannot be called without using an `Expect` statement to define its mocked behavior.
    * A temporary marker is automatically removed when the Expectise session is torn down.
    """
    method = Method(ref)
    marker = session.mark_method(method, trigger=AlwaysTrigger(), lifespan=Lifespan.TEMPORARY)
    marker.enable()
