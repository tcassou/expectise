import pytest
from some_module import some_functions

from expectise import disable_mock
from expectise import Expect
from expectise import mock
from expectise import tear_down
from expectise.exceptions import EnvironmentError
from expectise.exceptions import ExpectationError


"""
This example focuses on testing functions = callable objects that are not methods of a class.
We implement a Pytest fixture that enumerates methods to be mocked, and resets the mocking context
after each test by calling the `tear_down` function.
When tearing down, we resolve calls to methods that were expected (in the sense of described by an `Expect` statement)
but not performed.
"""


@pytest.fixture(autouse=True)
def run_around_tests():
    # You can insert code that will run before each test here, for example mocking a specific method
    # no preceded by a mock_if decorator
    mock(some_functions.my_root)
    mock(some_functions.my_product)
    # A test function will be run at this point
    yield
    # Tear down code that will run after each test
    tear_down()


def test_fixture_mock():
    # In this example, mocking happens inside a pytest fixture, that will perform some actions before and after each
    # test is executed. This is one way of mocking methods, that has the benefit of not interfering with "production"
    # code at all. On the other hand, it requires to enumerate mock statements any time they are needed,
    # while `mock_if` decorators are defined once and for all.
    Expect(some_functions.my_root).to_receive(4).and_return(12)
    assert some_functions.my_root(4) == 12

    Expect(some_functions.my_product).and_return(12)
    assert some_functions.my_product(4, 3) == 12


def test_function():
    # The `my_root` function is mocked, and without the appropriate `Expect` statement describing its expected
    # behavior in test environment, it will raise an error.
    with pytest.raises(EnvironmentError):
        some_functions.my_root(4)


def test_function_called():
    # The `my_root` function is mocked, an `Expect` statement is used, but it does not describe what the function
    # should perform. Therefore an exception is raised.
    Expect(some_functions.my_root)
    with pytest.raises(EnvironmentError):
        some_functions.my_root(4)


def test_function_called_with_args():
    # You can check that the correct arguments are passed to the function call. That said, for this example to work,
    # you still need to define what the mocked function should return: an `EnvironmentError` is raised.
    Expect(some_functions.my_root).to_receive(x=12)
    with pytest.raises(EnvironmentError):
        some_functions.my_root(x=12)

    # Note that in case the arguments passed do not match expectations, an `ExpectationError` is raised.
    Expect(some_functions.my_root).to_receive(x=12).and_return(-1)
    with pytest.raises(ExpectationError):
        some_functions.my_root(x=13)


def test_function_return():
    # Expecting the function `my_product` to be called, with specifc arguments passed to it, and overriding its
    # behavior to return a desired output. This test case checks that the function is called, with the right input,
    # and modifies its return value(s). Can be useful in case the `my_product` performs a call to an external
    # service that you want to avoid in test environment, and therefore want to mock the response with your output.
    Expect(some_functions.my_product).to_receive(3, 3).and_return(12)
    # This example is silly of course. Instead, some more complex logic in your module would trigger the call
    # to `my_product` with the specific input you expect. Here, we mock the output with a `return 12`.
    assert some_functions.my_product(3, 3) == 12


def test_function_called_twice_error():
    # With the same setup as above, calling the same function a second time will raise an error. 2 `Expect`
    # statements are required for that.
    Expect(some_functions.my_product).to_receive(4, 3).and_return(16)
    some_functions.my_product(4, 3)
    with pytest.raises(ExpectationError):
        some_functions.my_product(4, 3)


def test_function_called_twice():
    # Same setup again, but this time several `Expect` statements properly describe the expected behavior.
    Expect(some_functions.my_product).to_receive(4, 3).and_return(15)
    Expect(some_functions.my_product).to_receive(4, 3).and_return(13)
    assert some_functions.my_product(4, 3) == 15
    assert some_functions.my_product(4, 3) == 13


def test_function_raise():
    # Expecting the function `my_root` to be called, with specifc arguments passed to it, and overriding its
    # behavior to raise the desired error. This test case checks that the function is called, with the right input,
    # and modifies its behavior. Can be useful to ensure that your code handles exceptions gracefully.
    Expect(some_functions.my_root).to_receive(4).and_raise(ZeroDivisionError("How can it be!?"))
    # Again, silly example, just to illustrate what can be done with the framework.
    with pytest.raises(ZeroDivisionError):
        some_functions.my_root(4)


def test_function_return_only():
    # Similar example as above, with no check of arguments passed to `my_product`.
    Expect(some_functions.my_product).to_return(42)
    assert some_functions.my_product(4, 3) == 42


def test_function_raise_only():
    # Similar example as above, with no check of arguments passed to `my_product`.
    Expect(some_functions.my_product).to_raise(ZeroDivisionError("How can it be!?"))
    with pytest.raises(ZeroDivisionError):
        some_functions.my_product(4, 3)


def test_disable():
    # Trying to disable a non-existing Mock
    with pytest.raises(EnvironmentError):
        disable_mock(some_functions.my_division)

    # Disabling the mock should allow setting the property
    disable_mock(some_functions.my_root)
    assert some_functions.my_root(4) == 2
