import os
from typing import Callable
from typing import Type

from .exceptions import EnvironmentError
from .expect import Expect


class Mock:
    """Represent a mocked method and its behaviour depending on the environment context."""

    def __init__(self, klass: Type, method: Callable, env_name: str, env_value: str) -> None:
        self.klass = klass
        self.method = method
        self.is_classmethod = isinstance(method, classmethod)
        self.is_staticmethod = isinstance(method, staticmethod)
        self.is_property = isinstance(method, property)
        self.env_name = env_name
        self.env_value = env_value

    @property
    def name(self) -> str:
        """Return the mocked method name, depending on the type of method mocked."""
        if self.is_classmethod or self.is_staticmethod:
            return self.method.__func__.__name__
        if self.is_property:
            return self.method.fget.__name__
        return self.method.__name__

    @property
    def surrogate(self):
        """Return a surrogate function that will replace the mocked method under the right environment context."""

        def func(*args, **kwargs):
            raise EnvironmentError(
                f"""
                Method `{self.name}` from class `{self.klass.__name__}` is mocked when {self.env_name}={self.env_value},
                and will raise errors if called without using an `Expect` statement to define its mocked behavior.
                """
            )

        if self.is_classmethod:
            return classmethod(func)
        if self.is_staticmethod:
            return staticmethod(func)
        if self.is_property:
            return property(func)
        return func

    def disable(self):
        """Restore the original method and remove any mocking logic."""
        setattr(self.klass, self.name, self.method)

    def enable(self):
        """Replace the mocked method with its surrogate."""
        Expect.set_up(self)


def mock(klass: Type, method: Callable, env_name: str, env_value: str) -> None:
    """Enable mocking of an object method by replacing it with a surrogate, requiring subsequent `Expect` statements."""
    Mock(klass, method, env_name, env_value).enable()


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
            self.mock = Mock(None, method, env_name, env_value)

        def __set_name__(self, owner: Type, name: str) -> None:
            """
            At interpretation time when the MockDecorator object is created, the surrounding class is not created yet.
            As soon as it is, this `__set_name__` method is called, which gives us a way to know and record the class or
            object that owns the method.
            """
            self.mock.klass = owner
            # In any environment that is not our test environment, we do not interfere with the method definition.
            if os.environ.get(env_name, "") != env_value:
                self.mock.disable()
                return

            # In test environment, the mocked methods are replaced by placeholders that raise errors if called without
            # the prior use of an `Expect` statement to define how they should behave during tests.
            self.mock.enable()

    return MockDecorator


def tear_down():
    """Reset mocking behaviour so that further tests can be run without any interference."""
    Expect.tear_down()
