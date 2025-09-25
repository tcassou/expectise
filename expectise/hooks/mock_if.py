from typing import Callable
from typing import Type

from expectise.exceptions import EnvironmentError
from expectise.lib.session import session
from expectise.models import Lifespan
from expectise.models.method import Method
from expectise.models.trigger import EnvTrigger


def mock_if(env_key: str, env_val: str) -> Type:
    """
    Decorator to identify which methods should be mocked permanently, depending on the environment.
    * The marker is activated only in case the environment conditions are met.
    * Once marked, a method cannot be called without using an `Expect` statement to define its mocked behavior.
    * A permanent marker is not removed when the Expectise session is torn down (but related mocks are reset).

    Example:

        mock_if("ENV", "test")
        def foo(...)
            pass

    """

    class MockDecorator:
        def __init__(self, ref: Callable) -> None:
            """
            Decorator class, that takes as input the method to be mocked:
            * if the environment conditions are met, the method is effectively marked as mocked,
            * if not, the method is left unchanged.
            """
            self.method = Method(ref)
            self._original_id = self.method.id
            self.marker = session.mark_method(
                self.method,
                trigger=EnvTrigger(env_key, env_val),
                lifespan=Lifespan.PERMANENT,
            )

        def __set_name__(self, owner: Type, name: str) -> None:
            """
            At interpretation time when the MockDecorator object is created, the surrounding class is not created yet.
            As soon as it is, this `__set_name__` method is called, which gives us a way to know and record the class or
            object that owns the method.
            """
            self.method.klass = owner
            self.marker.enable()

        def __call__(self, *args, **kwargs) -> Callable:
            """ """
            # Function markers cannot be enabled at interpretation time like method markers can.
            # Such markers are enabled later, when `Expect` statements are used to define the mocked behavior.
            # If the function is called without using an `Expect` statement to define its mocked behavior,
            # we need to raise an error, unless the marker was explicitly disabled.
            if not self.marker.enabled and not self.marker.disabled:
                raise EnvironmentError(
                    f"Method `{self.method.id}` is marked as mocked, "
                    "and will raise errors if called without using an `Expect` statement to define its mocked behavior."
                )

            return getattr(self.method.owner, self.method.name)(*args, **kwargs)

    return MockDecorator
