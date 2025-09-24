from typing import Callable
from typing import Type

from .models import Lifespan
from .models.method import Method
from .models.trigger import AlwaysTrigger
from .models.trigger import EnvTrigger
from expectise.mock.session import session


def mock(ref: Callable) -> None:
    """
    Mark a method as temporarily mocked.
    * Once marked, a method cannot be called without using an `Expect` statement to define its mocked behavior.
    * A temporary marker is automatically removed when the Expectise session is torn down.
    """
    method = Method(ref)
    marker = session.mark_method(method, trigger=AlwaysTrigger(), lifespan=Lifespan.TEMPORARY)
    marker.enable()


def disable_mock(mock_ref: Callable) -> None:
    """
    Disable a mock marker, given the mocked method reference.
    This is useful for disabling a permanent mock marker that was created with the `mock_if` decorator.
    Once the marker is disabled, the method can be called and tested without any alteration of its behavior.
    """
    session.get_marker(mock_ref).disable()


def tear_down():
    """Reset mocking behavior so that further tests can be run without any interference."""
    session.tear_down()


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
