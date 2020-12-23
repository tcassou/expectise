import os

from .exceptions import EnvironmentError
from .expect import Expect


def mock_if(env_name, env_value):
    """
    Decorator to identify which methods should be mocked, only in case the right environment variable is set to the
    right value (for example, ENV=test).

    :param env_name: name of the environment variable to inspect
    :type env_name: str
    :param env_value: value to compare the environment variable env_name with
    :type env_value: str

    :return: the decorator class that implements the mocking logic
    :rtype: MockDecorator
    """

    class MockDecorator:
        def __init__(self, method):
            """
            Decorator class, that takes as input the method to be mocked:
            * if the environment conditions are met, the method is marked as to be mocked for later calls
            * if not, the method is left unchanged.

            :param method: the method to mock in test environment
            :type method: callable

            :return: None
            """
            self.method = method
            self.owner = None
            if isinstance(method, classmethod) or isinstance(method, classmethod):
                self.method_name = method.__func__.__name__
            else:
                self.method_name = method.__name__

        def __set_name__(self, owner, name):
            """
            At interpretation time when the MockDecorator object is created, the surrounding class is not created yet.
            As soon as it is, this `__set_name__` method is called, which gives us a way to know and record the class or
            object that owns the method.

            :param owner: the class or object owning the method
            :type owner: object
            :param name: the name of the method
            :type name: str

            :return: None
            """
            self.owner = owner
            # In any environment that is not our test environment, we do not interfere with the method definition.
            if os.environ.get(env_name, "") != env_value:
                setattr(owner, name, self.method)
                return

            # In test environment, we mark the object owning the mocked method as owning mocked elements
            if owner.__name__ not in Expect.class_h:
                Expect.class_h[owner.__name__] = owner
            # and we mark the method itself as mocked, to alter its behavior and watch its calls
            Expect.method_h[(owner.__name__, name)] = {"method": self.method, **Expect.init_args()}

        def __call__(self, *args, **kwargs):
            """
            In test environment, the mocked methods are replaced by an instance of MockDecorator. This method makes
            them callable, in order to raise errors if called without the prior definition of an `Expect` statement
            to define how they should behave during the tests being run.

            :param args: positional arguments
            :type args: [object]
            :param kwargs: keyword arguments
            :type kwargs: {str: object}

            :return: None
            """
            raise EnvironmentError(
                f"""
                Method `{self.method_name}` from class `{self.owner.__name__}` is mocked when {env_name}={env_value},
                and will raise errors if called without using an `Expect` statement to define its mocked behavior.
                """
            )

    return MockDecorator
