from typing import Callable
from typing import Type

from expectise.exceptions import EnvironmentError
from expectise.lib.session import session
from expectise.models import Lifespan
from expectise.models.kallable import Kallable
from expectise.models.trigger import EnvTrigger


def mock_if(env_key: str, env_val: str) -> Type:
    """
    Decorator to identify which functions or class methods should be mocked permanently, depending on the environment.
    * The marker is activated only in case the environment conditions are met.
    * Once marked, a function or method cannot be called without using an `Expect` statement to define its behavior.
    * A permanent marker is not removed when the Expectise session is torn down (but related mocks are reset).

    Example:

        mock_if("ENV", "test")
        def foo(...)
            pass

    """

    class MockDecorator:
        def __init__(self, ref: Callable) -> None:
            """
            Decorator class, that takes as input the function or class method to be mocked:
            * if the environment conditions are met, the function or class method is effectively marked as mocked,
            * if not, the function or class method is left unchanged.
            """
            self.kallable = Kallable(ref)
            self._original_id = self.kallable.id
            self.marker = session.mark_method(
                self.kallable,
                trigger=EnvTrigger(env_key, env_val),
                lifespan=Lifespan.PERMANENT,
            )

        def __set_name__(self, owner: Type, name: str) -> None:
            """
            Applies to class methods only.
            At interpretation time when the MockDecorator object is created, the surrounding class is not created yet.
            As soon as it is, this `__set_name__` method is called, which gives us a way to know and record the class
            that owns the method to be mocked.
            """
            self.kallable.klass = owner
            self.marker.set_up()

        def __repr__(self) -> str:
            return self.kallable.ref.__repr__()

        def __call__(self, *args, **kwargs) -> Callable:
            """
            Applies to standalone functions only.
            Function markers cannot be enabled at interpretation time like method markers can.
            Such markers are enabled later, when `Expect` statements are used to define the mocked behavior.
            If the function is called without using an `Expect` statement to define its mocked behavior,
            we need to raise an error, unless the marker was explicitly disabled.
            """
            self.marker.set_up()
            # For standalone functions decorated with `mock_if`, when environment conditions are not met,
            # the original function should be called. This block will be executed only once, and further calls
            # to the function will
            if not self.marker.enabled:
                return self.kallable.ref(*args, **kwargs)

            # If the trigger is met, this block should never be reached:
            # * the marker is either enabled, in which case the function override is already applied,
            # * or the marker is explicitly disabled, in which case the original function should be called.
            raise EnvironmentError(
                f"Callable `{self.kallable.id}` is marked as mocked, "
                "and will raise errors if called without using an `Expect` statement to define its mocked behavior."
            )

    return MockDecorator
