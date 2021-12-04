# -*- coding: utf-8 -*-
from .diff import Diff
from .exceptions import EnvironmentError
from .exceptions import ExpectationError


class Expect(object):
    """
    Mocking function calls for Unit tests purposes, refer to the README for more details and examples.
    """

    # Dict of classes with at least one method mocked, shared between Expect instances: {'class_name': class}
    class_h = {}
    # Dict of mocked methods, with potential arguments and outputs, shared between Expect instances):
    # {
    #   ('class_name', 'method_name'):
    #     {
    #       'method': callable_object,                      --> Method to decorate (original method)
    #       'expected': int,                                --> Expected number of calls to the method
    #       'performed': int,                               --> Performed number of calls to the method
    #       'decorators': [callable_object]                 --> list of decorators to apply to the original method
    #       'with_args': [((object), {string: object})],    --> list of (args, kwargs) the method should be called with
    #       'return': [object],                             --> list of outputs the decorated method should return
    #     }
    # }
    method_h = {}

    def __init__(self, class_name):
        """Init

        :param str class_name: name of the class

        :return: None
        """
        if class_name not in Expect.class_h:
            raise EnvironmentError(
                f"""
                No method of class `{class_name}` is mocked, so this instantiation is not allowed.
                Check that the right environment variable is set, and that the right methods from `{class_name}`
                are decorated with `@mock_if(your_env_variable_name, your_env_variable_value)`.
                """
            )
        self.klass = Expect.class_h[class_name]
        self.method_name = None
        self.method = None
        self.is_classmethod = False
        self.is_staticmethod = False
        self.decorator_names = ["raise", "return", "with_args", "classmethod", "staticmethod"]  # Order matters!
        self.decorators = {decorator_name: None for decorator_name in self.decorator_names}

    def get_decoration(self):
        """Get the right decoration of the original method, depending on the number of calls already performed.

        :return: the right decorated method
        :rtype: callable object
        """
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] - 1
        return Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][call_idx]

    def override_method(self):
        """Override the original method in order to pick the right decorated method and apply it instead.
        Check that the method is called (and the right number of times) is done here.

        :return: a decorated method
        :rtype: callable object
        """

        def func(*args, **kwargs):
            self.mark_received()
            decorated = self.get_decoration()
            decorated = decorated.__func__ if self.is_staticmethod or self.is_classmethod else decorated
            return decorated(*args, **kwargs)

        if self.is_staticmethod:
            return staticmethod(func)
        elif self.is_classmethod:
            return classmethod(func)
        return func

    def is_decorated(self, method):
        """Checking for existing decorators around the target method: classmethod or staticmethod.

        :param callable object method: method to check

        :return: True if the method is decorated, False otherwise
        :rtype: bool
        """
        if isinstance(method, classmethod):
            self.decorators["classmethod"] = classmethod
            self.is_classmethod = True
        if isinstance(method, staticmethod):
            self.decorators["staticmethod"] = staticmethod
            self.is_staticmethod = True
        return self.is_classmethod or self.is_staticmethod

    def decorate(self):
        """Iteratively apply active decorators to the target method.

        :return: decorated method
        :rtype: method
        """
        method = self.method.__func__ if self.is_decorated(self.method) else self.method
        for decorator_name in self.decorator_names:
            decorator = self.decorators[decorator_name]
            method = decorator(method) if decorator else method
        return method

    def mark_received(self):
        """Mark decorated method as called once more, and raise exception if it is called more times than expected.

        :return: None
        """
        Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] += 1
        perf = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"]
        exp = Expect.method_h[(self.klass.__name__, self.method_name)]["expected"]
        if perf > exp:
            raise ExpectationError(
                "{}.{} is expected to be called {} time(s) only.".format(self.klass.__name__, self.method_name, exp)
            )

    def to_receive(self, method_name):
        """Decorating a method to check that it is called.

        :param str method_name: name of the method

        :return: Expect object
        :rtype: Expect
        """
        key = (self.klass.__name__, method_name)
        self.method_name = method_name
        self.method = Expect.method_h[key]["method"]
        if key not in Expect.method_h:
            raise EnvironmentError(
                f"""
                Method `{method_name}` from class `{self.klass.__name__}` is not mocked.
                Decorate it with @mock_if(your_env_variable_name, your_env_variable_value) to be able to mock its calls.
                """
            )
        else:
            Expect.method_h[key]["expected"] += 1
            Expect.method_h[key]["decorators"].append(None)
            Expect.method_h[key]["with_args"].append(None)
            Expect.method_h[key]["return"].append(None)

        # Setting up decoration
        Expect.method_h[key]["decorators"][-1] = self.decorate()
        setattr(self.klass, self.method_name, self.override_method())
        return self

    def assert_arguments(self, func_args, func_kwargs):
        """Asserting equality of arguments.

        :param [object] func_args: list of passed arguments
        :param {string: object} func_kwargs: dict of passed keyword arguments

        :return: None
        """
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] - 1
        args, kwargs = Expect.method_h[(self.klass.__name__, self.method_name)]["with_args"][call_idx]

        msg = f"`{self.method_name}` method of `{self.klass.__name__}` called with " + "unexpected {} arguments:\n\n"
        if args != func_args:
            raise ExpectationError(msg.format("positional") + Diff.print(args, func_args))
        if kwargs != func_kwargs:
            raise ExpectationError(msg.format("keyword") + Diff.print(kwargs, func_kwargs))

    def with_args_decorator(self, method):
        """Decorator to check passed argument.

        :param callable object method: method to decorate

        :return: decorated method
        :rtype: method
        """

        def instance_func(obj, *func_args, **func_kwargs):
            self.assert_arguments(func_args, func_kwargs)
            return method(obj, *func_args, **func_kwargs)

        def static_func(*func_args, **func_kwargs):
            self.assert_arguments(func_args, func_kwargs)
            return method(*func_args, **func_kwargs)

        return static_func if self.is_staticmethod else instance_func

    def with_args(self, *args, **kwargs):
        """Decorating a method to check it is called with the desired arguments.

        :param [object] args: list of arguments
        :param {string: object} kwargs: dict of keyword arguments

        :return: Expect object
        :rtype: Expect
        """
        if self.method is None:
            raise ExpectationError("Expect error: calling .with_args() without prior call of to_receive()")
        self.decorators["with_args"] = self.with_args_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]["with_args"][-1] = (args, kwargs)
        Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][-1] = self.decorate()
        return self

    def get_output(self):
        """Get the right output to return when .and_return() decoration is used.

        :return: output
        :rtype: object
        """
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]["performed"] - 1
        return Expect.method_h[(self.klass.__name__, self.method_name)]["return"][call_idx]

    def return_decorator(self, method):
        """Decorator to modify objects returned.

        :param callable object method: method to decorate

        :return: decorated method
        :rtype: method
        """

        def func(*func_args, **func_kwargs):
            return self.get_output()

        return func

    def and_return(self, output):
        """Overwrite a method to output the object passed as argument.

        :param object output: the desired output

        :return: Expect object
        :rtype: Expect
        """
        if self.method is None:
            raise ExpectationError("Expect error: calling and_return() without prior call of to_receive()")
        self.decorators["return"] = self.return_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]["return"][-1] = output
        Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][-1] = self.decorate()
        return self

    def raise_decorator(self, method):
        """Decorator to raise errors.

        :param callable object method: method to decorate

        :return: decorated method
        :rtype: method
        """

        def func(*func_args, **func_kwargs):
            raise self.get_output()

        return func

    def and_raise(self, error):
        """Overwrite a method to raise an error when called.

        :param Exception error: the error to raise

        :return: Expect object
        :rtype: Expect
        """
        if self.method is None:
            raise ExpectationError("Expect error: calling and_raise() without prior call of to_receive()")
        self.decorators["raise"] = self.raise_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]["return"][-1] = error
        Expect.method_h[(self.klass.__name__, self.method_name)]["decorators"][-1] = self.decorate()
        return self

    @classmethod
    def set_up(cls, klass, method_name, surrogate):
        """
        Set up the `Expect` context and replace the method being mocked with a surrogate function.
        This method is called at interpretation time as `mock_if` statements are being resolved, and at the end
        of each unit test to start the next one with a clean context.

        :param klass: class object owning the mocked method
        :type klass: object
        :param method_name: name of the mocked method
        :type method_name: str
        :param surrogate: the method to use as surrogate for the method being mocked
        :type surrogate: callable

        :return: None
        """
        # When called from `mock_if` decorating statement, adding classes to the list of altered objects
        if klass.__name__ not in cls.class_h:
            cls.class_h[klass.__name__] = klass

        # Initializing the Expect context
        cls.method_h[(klass.__name__, method_name)] = {
            "method": surrogate,
            "expected": 0,
            "performed": 0,
            "decorators": [],
            "with_args": [],
            "return": [],
        }
        # Substituting original methods with surrogates that raise errors if not preceded by `Expect` statements
        setattr(klass, method_name, surrogate)

    @classmethod
    def tear_down(cls):
        """
        Check for any method called less times than expected, and raise an AssertionError is any is found.
        """
        message = ""
        for (class_name, method_name), args in cls.method_h.items():
            remain = args["expected"] - args["performed"]
            if remain > 0:
                message += f"`{method_name}` from class `{class_name}` still expected to be called {remain} time(s).\n"
            # Resetting Expect parameters and original methods
            cls.set_up(cls.class_h[class_name], method_name, args["method"])

        # If some calls are still expected, message is not empty, so asserting False with the appropriate message
        assert not message, message
