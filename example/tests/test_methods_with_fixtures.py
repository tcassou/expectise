import pytest
from some_module.some_api import SomeAPI
from some_module.some_other_api import SomeOtherAPI

from expectise import disable_mock
from expectise import Expect
from expectise import mock
from expectise import tear_down
from expectise.exceptions import EnvironmentError
from expectise.exceptions import ExpectationError


"""
This example focuses on testing methods of a class.
We implement a Pytest fixture that enumerates methods to be mocked, and resets the mocking context
after each test by calling the `tear_down` function.
When tearing down, we resolve calls to methods that were expected (in the sense of described by an `Expect` statement)
but not performed.
"""


@pytest.fixture(autouse=True)
def run_around_tests():
    # You can insert code that will run before each test here, for example mocking a specific method
    # no preceded by a mock_if decorator
    mock(SomeOtherAPI.do_advanced_stuff)
    mock(SomeOtherAPI.secret_info)
    # A test function will be run at this point
    yield
    # Tear down code that will run after each test
    tear_down()


def test_fixture_mock():
    # In this example, mocking happens inside a pytest fixture, that will perform some actions before and after each
    # test is executed. This is one way of mocking methods, that has the benefit of not interfering with "production"
    # code at all. On the other hand, it requires explicit imports and references, while `mock_if` decorators (see
    # below examples) are explicit and concise.
    Expect(SomeOtherAPI.do_advanced_stuff).to_receive("bar").and_return("it works!")
    api = SomeOtherAPI()
    assert api.do_advanced_stuff("bar") == "it works!"

    Expect(SomeOtherAPI.secret_info).to_return("********")
    assert api.secret_info == "********"


def test_method():
    # The `get_something` method is mocked, and without the appropriate `Expect` statement describing its expected
    # behavior in test environment, it will raise an error.
    with pytest.raises(EnvironmentError):
        SomeAPI.get_something("foo", "bar")


def test_method_called():
    # The `do_something_else` method is mocked, an `Expect` statement is used, but it does not describe what the method
    # should perform. Therefore an exception is raised.
    Expect(SomeAPI.do_something_else)
    with pytest.raises(EnvironmentError):
        SomeAPI.do_something_else()


def test_method_called_with_args():
    # You can check that the correct arguments are passed to the method call. That said, for this example to work,
    # you still need to define what the mocked method should return: an `EnvironmentError` is raised.
    Expect(SomeAPI.do_something_else).to_receive(x=12)
    with pytest.raises(EnvironmentError):
        SomeAPI.do_something_else(x=12)

    # Note that in case the arguments passed do not match expectations, an `ExpectationError` is raised.
    Expect(SomeAPI.do_something_else).to_receive(x=12).and_return(True)
    with pytest.raises(ExpectationError):
        SomeAPI.do_something_else(x=13)


def test_method_return():
    # Expecting the method `get_something` to be called, with specifc arguments passed to it, and overriding its
    # behavior to return a desired output. This test case checks that the method is called, with the right input,
    # and modifies its return value(s). Can be useful in case the `get_something` performs a call to an external
    # service that you want to avoid in test environment, and therefore want to mock the response with your output.
    Expect(SomeAPI.get_something).to_receive("foo", "bar").and_return(False)
    # This example is silly of course. Instead, some more complex logic in your module would trigger the call
    # to `get_something` with the specific input you expect. Here, we mock the output with a `return False`.
    assert not SomeAPI.get_something("foo", "bar")


def test_method_called_twice():
    # With the same setup as above, calling the same method a second time will raise an error. 2 `Expect`
    # statements are required for that.
    Expect(SomeAPI.get_something).to_receive("foo", "bar").and_return(False)
    SomeAPI.get_something("foo", "bar")
    with pytest.raises(ExpectationError):
        SomeAPI.get_something("foo", "bar")


def test_method_raise():
    # Expecting the method `get_something` to be called, with specifc arguments passed to it, and overriding its
    # behavior to raise the desired error. This test case checks that the method is called, with the right input,
    # and modifies its behavior. Can be useful to ensure that your code handles exceptions gracefully.
    Expect(SomeAPI.get_something).to_receive("foo", "bar").and_raise(ValueError("My error"))
    # Again, silly example, just to illustrate what can be done with the framework.
    with pytest.raises(ValueError):
        SomeAPI.get_something("foo", "bar")


def test_method_return_only():
    # Similar example as above, with no check of arguments passed to `get_something`.
    Expect(SomeAPI.get_something).to_return(42)
    assert SomeAPI.get_something("foo", "bar") == 42


def test_method_raise_only():
    # Similar example as above, with no check of arguments passed to `get_something`.
    Expect(SomeAPI.get_something).to_raise(ValueError("My error"))
    with pytest.raises(ValueError):
        SomeAPI.get_something("python", "snake")


def test_static_method():
    # Everything works with staticmethods
    Expect(SomeAPI.compute_sum).to_receive(1, 2).and_return(4)
    assert SomeAPI.compute_sum(1, 2) == 4


def test_instance_method():
    # Everything works with instance methods
    Expect(SomeAPI.update_attribute).to_return("sshhhh")
    assert SomeAPI().update_attribute("secret_value") == "sshhhh"


def test_property():
    # Everything works with properties
    Expect(SomeAPI.some_property).to_return("bar")
    assert SomeAPI().some_property == "bar"


def test_disable():
    # Trying to disable a non-existing Mock
    with pytest.raises(EnvironmentError):
        disable_mock(SomeAPI.unmocked_method)

    some_api = SomeAPI()

    # Disabling the mock should allow setting the property
    disable_mock(SomeAPI.update_attribute)
    some_api.update_attribute("new_value")
    assert some_api.my_attribute == "new_value"

    # Same for some other API
    disable_mock(SomeOtherAPI.do_advanced_stuff)
    some_other_api = SomeOtherAPI(foo=5)
    val = some_other_api.do_advanced_stuff(bar="high")
    assert val == "high>>5"
