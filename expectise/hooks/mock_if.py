from typing import Callable
from typing import Type

from expectise.mock.session import session
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
            self.ref = ref

        def __set_name__(self, owner: Type, name: str) -> None:
            """
            At interpretation time when the MockDecorator object is created, the surrounding class is not created yet.
            As soon as it is, this `__set_name__` method is called, which gives us a way to know and record the class or
            object that owns the method.
            """
            method = Method(self.ref, owner=owner)
            marker = session.mark_method(method, trigger=EnvTrigger(env_key, env_val), lifespan=Lifespan.PERMANENT)
            # If the environment conditions are not met, the marker is disabled.
            if not marker.trigger.is_met():
                return

            # If the environment conditions are met, the mocked methods are replaced by placeholders that raise errors
            # if called without the prior use of an `Expect` statement to define how they should behave during tests.
            marker.enable()

    return MockDecorator
