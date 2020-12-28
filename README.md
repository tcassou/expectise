# Expectise
![Lint, Test and Release](https://github.com/tcassou/expectise/workflows/Lint,%20Test%20and%20Release/badge.svg?branch=master)

Mocking function calls in Python - inspired by Ruby's RSpec-Mocks.

## Description
Test environments are usually isolated from external services, and meant to check the execution logic of the code exclusively. However it is quite common for projects to deal with external APIs (to receive or post data for example) or systems (such as databases).
In that scenario, there are (at least) 2 options:
1. not testing such modules or objects to avoid performing external calls (that would fail anyway - ideally),
2. mocking external calls in order to test their surrounding logic, and increase the coverage of tests as much as possible.

This package is here to help with 2).

## Contents
This repo contains:
* the `expectise` module itself, under `/expectise`;
* a dummy example of small module with its tests under `/example` with unit tests showcasing what the `expectise` package can do.

## Install
Install from [Pypi](https://pypi.org/project/expectise/):
```bash
pip install expectise
```

## Running Tests with Expectise
There are 2 ways of setting up your tests to work with `expectise`:
1. By defining a teardown method for all your tests. See the example in [this file](https://github.com/tcassou/expectise/blob/master/example/tests/my_test_case.py), with [`nose`](https://nose.readthedocs.io/en/latest/) as a test framework. We recommend using this approach if most of your tests manipulate objects that you want to mock. [This test file](https://github.com/tcassou/expectise/blob/master/example/tests/some_file_test.py) shows a few practical examples of meaningful `Expect` statements.
2. By using the `Expectations` context manager provided in this package. We recommend using this approach if only a few of your tests deal with functions that you want to mock. [This test file](https://github.com/tcassou/expectise/blob/master/example/tests/some_other_file_test.py) shows examples of tests defined using this approach.

Regardless of the way you handle the context, you will lastly need to decorate the methods you want to mock in test environment. Simply use the `mock_if` decorator with the name and value of the environment variable you use to identify your test environment. This environment variable, say `ENV` will be checked at interpretation time: if its value matches the input, say `ENV=test`, the mocking logic will be implemented; if not, nothing in your code will be modified, and performance will stay the same since nothing will happen after interpretation!

Example of decoration:
```python
from expectise import mock_if


class MyObject:
    ...

    @mock_if("ENV", "test")
    def my_function(self, ...)
        ...

    ...
```

## Examples
The following use cases are covered:
* asserting that a method is called (the right number of times),
* checking the arguments passed to a method,
* overriding a method so that it returns a given output when called,
* overriding a method so that it raises an exception when called.

The above features can be combined too, with the following 4 possible patterns:
```python
Expect('MyObject').to_receive('my_method').and_return(my_object)
Expect('MyObject').to_receive('my_method').and_raise(my_error)
Expect('MyObject').to_receive('my_method').with_args(*my_args, **my_kwargs).and_return(my_object)
Expect('MyObject').to_receive('my_method').with_args(*my_args, **my_kwargs).and_raise(my_error)
```

A given method of a class can be decorated several times, with different arguments to check and ouputs to be returned.
You just have to specify it with several `Expect` statements. In this case, the order of the statements matters.

The following is valid and assumes `my_method` is going to be called three times exactly:
```python
Expect('MyObject').to_receive('my_method').with_args(*my_args_1, **my_kwargs_1).and_return(my_object_1)
Expect('MyObject').to_receive('my_method').with_args(*my_args_2, **my_kwargs_2).and_raise(my_error)
Expect('MyObject').to_receive('my_method').with_args(*my_args_3, **my_kwargs_3).and_return(my_object_2)
```

Note that if a method decorated at least once with an `Expect` statement is called more or less times than the number
of Expect statements, the unit test will fail.
