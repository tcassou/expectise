import os
from typing import Callable
from typing import Type

from .exceptions import EnvironmentError
from .expect import Expect


def mock_if(env_name: str, env_value: str) -> Type:
    """
    Decorator to identify which methods should be mocked, only in case the right environment variable is set to the
    right value. Example:

        mock_if("ENV", "test")
        def foo(...)
            pass
    """

    class MockDecorator:
        def __init__(self, method: Callable) -> None:
            """
            Decorator class, that takes as input the method to be mocked:
            * if the environment conditions are met, the method is marked as to be mocked for later calls
            * if not, the method is left unchanged.
            """
            self.method = method
            self.owner = None

        def __set_name__(self, owner: Type, name: str) -> None:
            """
            At interpretation time when the MockDecorator object is created, the surrounding class is not created yet.
            As soon as it is, this `__set_name__` method is called, which gives us a way to know and record the class or
            object that owns the method.
            """
            self.owner = owner
            # In any environment that is not our test environment, we do not interfere with the method definition.
            if os.environ.get(env_name, "") != env_value:
                setattr(owner, name, self.method)
                return

            # In test environment, the mocked methods are replaced by placeholders that raise errors if called without
            # the prior use of an `Expect` statement to define how they should behave during tests.
            Expect.set_up(owner, name, surrogate(owner, self.method, env_name, env_value))

    return MockDecorator


def surrogate(klass: type, method: Callable, env_name: str, env_value: str) -> Callable:
    """
    Define a surrogate function that will replace any mocked method, so that any call to the method raises an
    error if not preceded by the appropriate `Expect` statement.
    """
    is_classmethod = isinstance(method, classmethod)
    is_staticmethod = isinstance(method, staticmethod)
    method_name = method.__func__.__name__ if is_classmethod or is_staticmethod else method.__name__

    def func(*args, **kwargs):
        raise EnvironmentError(
            f"""
            Method `{method_name}` from class `{klass.__name__}` is mocked when {env_name}={env_value},
            and will raise errors if called without using an `Expect` statement to define its mocked behavior.
            """
        )

    if is_classmethod:
        return classmethod(func)
    if is_staticmethod:
        return staticmethod(func)
    return func
