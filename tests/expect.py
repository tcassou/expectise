# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import importlib
import inspect
import os
import models as models_package


# Dynamically importing all class objects from a given package (avoiding residual objecs from .pyc files).
models = {}
path = models_package.__path__[0]
for module_file in os.listdir(path):
    if module_file.endswith('.py') and not module_file.startswith('__'):
        module = importlib.import_module(models_package.__name__ + '.' + module_file.split('.')[0])
        for module_object_name, module_object in module.__dict__.iteritems():
            if inspect.isclass(module_object) and module_object.__module__ == module.__name__:
                models[module_object_name] = module_object


class Expect(object):
    """

    Unit tests purposes
        * asserting that a method is called
        * checking the arguments passed to that method
        * overriding the method output

    Typical usage:
        Expect('MyModel').to_receive('my_method')
        Expect('MyModel').to_receive('my_method').and_return(my_object)
        Expect('MyModel').to_receive('my_method').and_raise(my_error)
        Expect('MyModel').to_receive('my_method').with_args(*my_args, **my_kwargs)
        Expect('MyModel').to_receive('my_method').with_args(*my_args, **my_kwargs).and_return(my_object)
        Expect('MyModel').to_receive('my_method').with_args(*my_args, **my_kwargs).and_raise(my_error)

    A given method of a class can be decorated several times, with different arguments to check, and ouputs, each time.
    You just have to specify it with several Expect statements. In this case, the order of the statements matters.

    The following is valid:
        Expect('MyModel').to_receive('my_method').with_args(*my_args_1, **my_kwargs_1).and_return(my_object_1)
        Expect('MyModel').to_receive('my_method').with_args(*my_args_2, **my_kwargs_2).and_raise(my_error)
        Expect('MyModel').to_receive('my_method').with_args(*my_args_2, **my_kwargs_2).and_return(my_object_2)

    Note that if a method decorated at least once with an Expect statement is called more or less times than the number
    of Expect statements, the unit test will fail.

    """

    # Hash of methods to be called, with potential arguments and outputs (shared between Expect instances):
    #
    # {
    #   ('class_name', 'method_name'):
    #     {
    #       'method': callable_object,                      --> Method to decorate (original method in the model)
    #       'expected': int,                                --> Expected number of calls to the method
    #       'performed': int,                               --> Performed number of calls to the method
    #       'with_args': [((object), {string: object})],    --> list of (args, kwargs) the method should be called with
    #       'return': [object],                             --> list of outputs the decorated method should return
    #     }
    # }
    method_h = {}

    def __init__(self, class_name):
        """ Init

        :param str class_name: name of the class

        :return: None
        """
        self.klass = models[class_name]
        self.method_name = None
        self.method = None
        self.is_classmethod = False
        self.is_staticmethod = False
        self.decorator_names = ['raise', 'return', 'with_args', 'classmethod', 'staticmethod']    # Order matters!
        self.decorators = {decorator_name: None for decorator_name in self.decorator_names}

    def get_decoration(self):
        """ Get the right decoration of original model method, depending on the number of calls already performed.

        :return: the right decorated method
        :rtype: callable object
        """
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]['performed'] - 1
        return Expect.method_h[(self.klass.__name__, self.method_name)]['decorators'][call_idx]

    def override_method(self):
        """ Override original model method in order to pick the right decorated method and apply it instead.
        Check that the method is called (and the right number of times) is done here.

        :return: a decorated method
        :rtype: callable object
        """
        def func(*func_args, **func_kwargs):
            self.mark_received()
            decorated = self.get_decoration()
            decorated = decorated.__func__ if self.is_staticmethod or self.is_classmethod else decorated
            return decorated(*func_args, **func_kwargs)

        if self.is_staticmethod:
            return staticmethod(func)
        elif self.is_classmethod:
            return classmethod(func)
        return func

    def is_decorated(self, method):
        """ Checking for existing decorators around the target method: classmethod or staticmethod.

        :param callable object method: method to check

        :return: True if the method is decorated, False otherwise
        :rtype: bool
        """
        if isinstance(method, classmethod):
            self.decorators['classmethod'] = classmethod
            self.is_classmethod = True
        if isinstance(method, staticmethod):
            self.decorators['staticmethod'] = staticmethod
            self.is_staticmethod = True
        return self.is_classmethod or self.is_staticmethod

    def decorate(self):
        """ Iteratively apply active decorators to the target method.

        :return: decorated method
        :rtype: method
        """
        method = self.method.__func__ if self.is_decorated(self.method) else self.method
        for decorator_name in self.decorator_names:
            decorator = self.decorators[decorator_name]
            method = decorator(method) if decorator else method
        return method

    def mark_received(self):
        """ Mark decorated method as called once more, and raise exception if it is called more times than expected.

        :return: None
        """
        Expect.method_h[(self.klass.__name__, self.method_name)]['performed'] += 1
        perf = Expect.method_h[(self.klass.__name__, self.method_name)]['performed']
        exp = Expect.method_h[(self.klass.__name__, self.method_name)]['expected']
        if perf > exp:
            raise Exception(
                '{}.{} is expected to be called {} time(s) only.'.format(self.klass.__name__, self.method_name, exp))

    def to_receive(self, method_name):
        """ Decorating a method to check that it is called.

        :param str method_name: name of the method

        :return: Expect object
        :rtype: Expect
        """
        self.method_name = method_name
        key = (self.klass.__name__, method_name)
        if key not in Expect.method_h:
            self.method = self.klass.__dict__[self.method_name]
            Expect.method_h[key] = {
                'method': self.method,
                'expected': 1,
                'performed': 0,
                'decorators': [None],
                'with_args': [None],
                'return': [None],
            }
        else:
            Expect.method_h[key]['expected'] += 1
            Expect.method_h[key]['decorators'].append(None)
            Expect.method_h[key]['with_args'].append(None)
            Expect.method_h[key]['return'].append(None)
            self.method = Expect.method_h[key]['method']
        # Setting up decoration
        Expect.method_h[key]['decorators'][-1] = self.decorate()
        setattr(self.klass, self.method_name, self.override_method())
        return self

    def assert_arguments(self, func_args, func_kwargs):
        """ Asserting equality of arguments.

        :param [object] func_args: list of passed arguments
        :param {string: object} func_kwargs: dict of passed keyword arguments

        :return: None
        """
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]['performed'] - 1
        args, kwargs = Expect.method_h[(self.klass.__name__, self.method_name)]['with_args'][call_idx]
        assert args == func_args and kwargs == func_kwargs, \
            '<{}> method of class <{}> called with {} instead of expected {}'.format(
                self.method_name, self.klass.__name__, (func_args, func_kwargs), (args, kwargs))

    def with_args_decorator(self, method):
        """ Decorator to check passed argument.

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
        """ Decorating a method to check it is called with the desired arguments.

        :param [object] args: list of arguments
        :param {string: object} kwargs: dict of keyword arguments

        :return: Expect object
        :rtype: Expect
        """
        if self.method is None:
            raise Exception('Expect error: calling .with_args() without prior call of to_receive()')
        self.decorators['with_args'] = self.with_args_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]['with_args'][-1] = (args, kwargs)
        Expect.method_h[(self.klass.__name__, self.method_name)]['decorators'][-1] = self.decorate()
        return self

    def get_output(self):
        """ Get the right output to return when .and_return() decoration is used.

        :return: output
        :rtype: object
        """
        call_idx = Expect.method_h[(self.klass.__name__, self.method_name)]['performed'] - 1
        return Expect.method_h[(self.klass.__name__, self.method_name)]['return'][call_idx]

    def return_decorator(self, method):
        """ Decorator to modify objects returned.

        :param callable object method: method to decorate

        :return: decorated method
        :rtype: method
        """
        def func(*func_args, **func_kwargs):
            return self.get_output()

        return func

    def and_return(self, output):
        """ Overwrite a method to output the object passed as argument.

        :param object output: the desired output

        :return: Expect object
        :rtype: Expect
        """
        if self.method is None:
            raise Exception('Expect error: calling and_return() without prior call of to_receive()')
        self.decorators['return'] = self.return_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]['return'][-1] = output
        Expect.method_h[(self.klass.__name__, self.method_name)]['decorators'][-1] = self.decorate()
        return self

    def raise_decorator(self, method):
        """ Decorator to raise errors.

        :param callable object method: method to decorate

        :return: decorated method
        :rtype: method
        """
        def func(*func_args, **func_kwargs):
            raise self.get_output()

        return func

    def and_raise(self, error):
        """ Overwrite a method to raise an error when called.

        :param Exception error: the error to raise

        :return: Expect object
        :rtype: Expect
        """
        if self.method is None:
            raise Exception('Expect error: calling and_raise() without prior call of to_receive()')
        self.decorators['raise'] = self.raise_decorator
        Expect.method_h[(self.klass.__name__, self.method_name)]['return'][-1] = error
        Expect.method_h[(self.klass.__name__, self.method_name)]['decorators'][-1] = self.decorate()
        return self
