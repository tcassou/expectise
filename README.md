# Expectise
[![Lint, Test and Release](https://github.com/tcassou/expectise/actions/workflows/lint_test_release.yaml/badge.svg)](https://github.com/tcassou/expectise/actions/workflows/lint_test_release.yaml)

Mocking function and method calls in Python - inspired by Ruby's RSpec-Mocks.

## Description
Test environments are usually isolated from external services, and meant to check the execution logic of the code exclusively. However it is common for projects to deal with external APIs (to receive or post data for example) or systems (such as databases), which are not accessible in a test environment.

This package offers a simple, natural way to mock external calls in order to test their surrounding logic, and increase the coverage of tests as much as possible.

## Contents
This repo contains:
* the `expectise` module itself, under `/expectise`;
* a dummy example of small module and its tests under `/example` with unit tests showcasing what the `expectise` package can do. Each test case is generously commented to explain how the `expectise` package is used.

## Install
Install from [Pypi](https://pypi.org/project/expectise/):
```bash
pip install expectise
```

## Running Tests with Expectise

Mocking functions and methods follows 3 steps:
1. Markers: marking a function or method as mocked. Once marked, the function or method is replaced by a placeholder function, and its calls intercepted.
2. Expectations: describing the expected behavior of the mocked function or method inside the unit tests.
3. Teardown: resetting the mocking behaviour so that all unit tests are fully independent and don't interfere with each other. During that step, some infractions can be caught too, such as not having called a method that was supposed to be called.

### 1/ Markers
Functions and methods can be marked as mocked in 2 different ways, that are described below.

#### Permanent Markers
Using the `mock_if` decorator, along with the name and value of the environment variable you use to identify your test environment.
This environment variable, say `ENV`, will be checked at interpretation time: if its value matches the input, say `ENV=test`, the mocking logic will be implemented; if not, nothing in your code will be modified, and performance will stay the same since nothing will happen passed interpretation.

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

This approach is concise, explicit and transparent: you can identify mocked methods at a glance, and your tests can remain light without any setup logic. However, it means patching production code, and carrying a dependency on this package in your production environment, which may be seen as a deal breaker from an isolation of concerns perspective.

#### Temporary Markers
Using explicit `mock` statements when setting up your tests.
Before running individual tests, mocks can be injected explicitly, typically through fixtures if you're familiar with `pytest` (you'll find examples in `examples/tests/`).

Example of statement:
```python
import pytest
from expectise import mock


@pytest.fixture(autouse=True)
def run_around_tests():
    mock(SomeObject.some_method)
    yield
    # see next section for more details on tear down actions
```

This approach is a little bit heavier, and may require more maintenance when mocked objects are modified. However, it keeps a clear separation of concerns, with production code that is not altered and does not have to depend on this package.

### 2/ Expectations
The following use cases are covered:
* asserting that a function or method is called (the right number of times),
* checking the arguments passed to a function or method,
* overriding a function or method so that it returns a given output when called,
* overriding a function or method so that it raises an exception when called.

The above features can be combined too, with the following 4 possible patterns:
```python
Expect(MyObject.my_method).to_return(my_object)
Expect(MyObject.my_method).to_raise(my_error)
Expect(MyObject.my_method).to_receive(*my_args, **my_kwargs).and_return(my_object)
Expect(MyObject.my_method).to_receive(*my_args, **my_kwargs).and_raise(my_error)
```

A given function or class method can be decorated several times, with different arguments to check and ouputs to be returned.
You just have to specify it with several `Expect` statements. In this case, the order of the statements matters.

The following is valid and assumes `my_method` is going to be called three times exactly:
```python
Expect(MyObject.my_method).to_receive(*my_args_1, **my_kwargs_1).and_return(my_object_1)
Expect(MyObject.my_method).to_receive(*my_args_2, **my_kwargs_2).and_raise(my_error)
Expect(MyObject.my_method).to_receive(*my_args_3, **my_kwargs_3).and_return(my_object_2)
```

Note that if a function or class method decorated at least once with an `Expect` statement is called more or less times than the number
of Expect statements, the unit test will fail.
You may also face a situation where disabling a mock is useful - for example, to write a test for a function or method decorated with `mock_if`.
To achieve this, simply call `disable_mock(my_callable)`.

### 3/ Tear Down
Once a test has run, underlying `expectise` objects have to be reset so that 1) some final checks can happen, and 2) new tests can be run with no undesirable side effects from previous tests. There are 2 ways of performing the necessary tear down actions, described below.

#### 1. Using the `Expectations` context manager
We recommend using this approach if only a few of your tests deal with functions or class methods that you want to mock. Toy example:

```python
from expectise import Expect
from some_module.some_api import SomeAPI


def test_instance_method():
    with Expectations():
        Expect(SomeAPI).to_receive("update_attribute").and_return("sshhhh")
        ...
        assert SomeAPI().update_attribute("secret_value") == "sshhhh"
```


#### 2. Calling `tear_down` explicitly
We recommend using this approach if most of your tests manipulate objects that you want to mock. Reusing the `pytest` fixtures example from the previous section:

```python
import pytest
from expectise import mock
from expectise import tear_down


@pytest.fixture(autouse=True)
def run_around_tests():
    mock(SomeObject.some_method)
    yield
    tear_down()
```

# Contributing
## Local Setup
We recommend [using `asdf` for managing high level dependencies](https://asdf-vm.com/).
With `asdf` installed,
1. simply run `asdf install` at the root of the repository,
2. run `poetry install` to install python dependencies.

## Running Tests
```python
eval $(poetry env activate)
ENV=test python -m pytest -v example/tests/
```
