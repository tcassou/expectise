# Expectise
![Lint, Test and Release](https://github.com/tcassou/expectise/workflows/Lint,%20Test%20and%20Release/badge.svg?branch=master)

Mocking function calls in Python - inspired by Ruby's RSpec-Mocks.

The content of this repo is an example of project, containing a `models` and a `tests` modules:

* `models` defines API classes, used to get / post / update / delete data;
* `tests` defines the project unit tests.

This **expectise** module allows to mock and/or listen to API calls for the purposes of unit tests, assuming that a test database or API is not always available.

## Install
Install from [Pypi](https://pypi.org/project/expectise/):
```
pip install expectise
```

## Context Management

## Examples
The following use cases are covered:

* asserting that a method is called (the right number of times),
* checking the arguments passed to a method,
* overriding a method so that it returns a given output when called,
* overriding a method so that it raises an exception when called.

The above features can be combined too, as shown below.

Typical usage:
```python
Expect('MyModel').to_receive('my_method')
Expect('MyModel').to_receive('my_method').and_return(my_object)
Expect('MyModel').to_receive('my_method').and_raise(my_error)
Expect('MyModel').to_receive('my_method').with_args(*my_args, **my_kwargs)
Expect('MyModel').to_receive('my_method').with_args(*my_args, **my_kwargs).and_return(my_object)
Expect('MyModel').to_receive('my_method').with_args(*my_args, **my_kwargs).and_raise(my_error)
```

A given method of a class can be decorated several times, with different arguments to check, and ouputs, each time.
You just have to specify it with several `Expect` statements. In this case, the order of the statements matters.

The following is valid (and assumes `my_method` is going to be called three times exactly):
```python
Expect('MyModel').to_receive('my_method').with_args(*my_args_1, **my_kwargs_1).and_return(my_object_1)
Expect('MyModel').to_receive('my_method').with_args(*my_args_2, **my_kwargs_2).and_raise(my_error)
Expect('MyModel').to_receive('my_method').with_args(*my_args_2, **my_kwargs_2).and_return(my_object_2)
```

Note that if a method decorated at least once with an `Expect` statement is called more or less times than the number
of Expect statements, the unit test will fail.
