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
* a dummy example of small module and its tests under `/example` with unit tests showcasing what the `expectise` package can do.

## Install
Install from [Pypi](https://pypi.org/project/expectise/):
```bash
pip install expectise
```

## Running Tests with Expectise

### Lifecycle
There are 2 steps in the lifecycle of decoration:
1. Set up: marking a method, so that it can be replaced by a surrogate method, and its calls intercepted;
2. Tear down: resetting the mocking behaviour so that all unit tests are fully independent and don't interfere with each other. During that step, some infractions can be caught too, such as not having called a method that was supposed to be called.

### Set Up
Methods can be marked as mocked in 2 different ways, that are described below.

1. Method 1: using the `mock_if` decorator, along with the name and value of the environment variable you use to identify your test environment.
This environment variable, say `ENV` will be checked at interpretation time: if its value matches the input, say `ENV=test`, the mocking logic will be implemented; if not, nothing in your code will be modified, and performance will stay the same since nothing will happen passed interpretation.

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

This method is concise, explicit and transparent: you can identify mocked candidates at a glance, and your tests can remain light without any heavy setup logic. However, it means patching production code, and carrying a dependency on this package in your production environment, which may be seen as a deal breaker from an isolation of concerns perspective.

2. Method 2: using explicit `mock` statements when setting up your tests.
Before running individual tests, mocks can be injected explicitly as part of any piece of custom logic, typically through fixtures if you're familiar with `pytest` (you'll find examples in `examples/tests/`).

Example of statement:
```python
import pytest
from expectise import mock


@pytest.fixture(autouse=True)
def run_around_tests():
    mock(SomeObject, SomeObject.some_method, "ENV", "test")
    yield
    # see next section for more details on tear down actions
```

This method is a little bit heavier, and may require more maintenance when mocked objects are modified. However, it keeps a clear separation of concerns with production code that is not patched and does not have to depend on this package.

### Tear Down
Once a test has run, underlying `expectise` objects have to be reset so that 1) some final checks can happen, and 2) new tests can be run with no undesirable side effects from previous tests. Again, there are 2 ways of performing the necessary tear down actions, described below.

1. Method 1: using the `Expectations` context manager provided in this package. We recommend using this approach if only a few of your tests deal with functions that you want to mock. Toy example:

```python
from expectise import Expect


def test_instance_method():
    with Expectations():
        Expect("SomeAPI").to_receive("update_attribute").and_return("sshhhh")
        ...
        assert SomeAPI().update_attribute("secret_value") == "sshhhh"
```

2. Method 2: by performing a teardown method for all your tests. We recommend using this approach if most of your tests manipulate objects that you want to mock. Reusing the `pytest` fixtures example from the previous section:

```python
import pytest
from expectise import mock
from expectise import tear_down


@pytest.fixture(autouse=True)
def run_around_tests():
    mock(SomeObject, SomeObject.some_method, "ENV", "test")
    yield
    tear_down()
```

## Mocking Examples
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
