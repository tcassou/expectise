import pytest
from some_module import some_functions

from expectise import disable_mock
from expectise import Expect
from expectise import Expectations
from expectise import mock
from expectise.exceptions import EnvironmentError
from expectise.exceptions import ExpectationError


"""
This example focuses on testing functions = callable objects that are not methods of a class.
We use the `Expectations` context manager to handle the tear down of our `Expect` objects.
When tearing down, we resolve calls to functions that were expected (in the sense of described by an `Expect` statement)
but not performed.
"""


def test_function():
    # The `my_sum` function is mocked, and without the appropriate `Expect` statement describing its expected
    # behavior in test environment, it will raise an error.
    with pytest.raises(EnvironmentError):
        some_functions.my_sum(1, 2)


def test_function_called():
    # The `my_square` function is mocked, an `Expect` statement is used, but it does not describe what the function
    # should perform. Therefore an exception is raised.
    with Expectations():
        Expect(some_functions.my_square)
        with pytest.raises(EnvironmentError):
            some_functions.my_square(1)


def test_function_called_with_args():
    # You can check that the correct arguments are passed to the function call. That said, for this example to work,
    # you still need to define what the mocked function should return: an `EnvironmentError` is raised.
    with Expectations():
        Expect(some_functions.my_square).to_receive(a=2)
        with pytest.raises(EnvironmentError):
            some_functions.my_square(a=12)

        # Note that in case the arguments passed do not match expectations, an `ExpectationError` is raised.
        Expect(some_functions.my_square).to_receive(a=2).and_return(8)
        with pytest.raises(ExpectationError):
            some_functions.my_square(a=4)


def test_function_return():
    # Expecting the function `my_sum` to be called, with specifc arguments passed to it, and overriding its
    # behavior to return a desired output. This test case checks that the function is called, with the right input,
    # and modifies its return value. Can be useful in case the `my_sum` performs a call to an external
    # service that you want to avoid in test environment, and therefore want to mock the response with your output.
    with Expectations():
        Expect(some_functions.my_sum).to_receive(1, 2).and_return(4)
        # This example is silly of course. Instead, some more complex logic in your module would trigger the call
        # to `my_sum` with the specific input you expect. Here, we mock the output with a `return 4`.
        assert some_functions.my_sum(1, 2) == 4


def test_function_called_twice_error():
    # With the same setup as above, calling the same function a second time will raise an error. 2 `Expect`
    # statements are required for that.
    with Expectations():
        Expect(some_functions.my_sum).to_receive(1, 2).and_return(4)
        some_functions.my_sum(1, 2)
        with pytest.raises(ExpectationError):
            some_functions.my_sum(1, 2)


def test_function_called_twice():
    # Same setup again, but this time several `Expect` statements properly describe the expected behavior.
    with Expectations():
        Expect(some_functions.my_sum).to_receive(1, 2).and_return(4)
        Expect(some_functions.my_sum).to_receive(1, 2).and_return(5)
        assert some_functions.my_sum(1, 2) == 4
        assert some_functions.my_sum(1, 2) == 5


def test_function_raise():
    # Expecting the function `my_sum` to be called, with specifc arguments passed to it, and overriding its
    # behavior to raise the desired error. This test case checks that the function is called, with the right input,
    # and modifies its behavior. Can be useful to ensure that your code handles exceptions gracefully.
    with Expectations():
        Expect(some_functions.my_sum).to_receive(1, 2).and_raise(ZeroDivisionError("Wait, what??"))
        # Again, silly example, just to illustrate what can be done with the framework.
        with pytest.raises(ZeroDivisionError):
            some_functions.my_sum(1, 2)


def test_function_return_only():
    # Similar example as above, with no check of arguments passed to `my_square`.
    with Expectations():
        Expect(some_functions.my_square).to_return(42)
        assert some_functions.my_square(2) == 42


def test_function_raise_only():
    # Similar example as above, with no check of arguments passed to `my_square`.
    with Expectations():
        Expect(some_functions.my_square).to_raise(ZeroDivisionError("Wait, what??"))
        with pytest.raises(ZeroDivisionError):
            some_functions.my_square(2)


def test_disable():
    # Disabling a permanentmock restores the original behavior of the function.
    with Expectations():
        disable_mock(some_functions.my_square)
        assert some_functions.my_square(2) == 4


def test_tear_down_disables_temporary_mocks():
    # This test ensures that calling mock(...) to create a temporary mock, and then tearing down (by exiting the
    # context manager) fully removes the mock and does not impact further tests
    with Expectations():
        mock(some_functions.my_root)
        Expect(some_functions.my_root).to_return(2)
        assert some_functions.my_root(8) == 2

    assert some_functions.my_root(4) == 2


def test_mock_function_with_local_reference():
    # This test is similar to the one above, but with a local reference to the function.
    # In that case, under the hood, the mock() statement replaces the `my_root` function inside the `some_functions`
    # module. But the import of the function creates a local reference to the function before replacement.
    # When calling `my_root(4)`, the local reference is used, and not the one inside the `some_functions` module,
    # and therefore the original function is called.
    # At the end, when tearing down, we're left with an expected call to `my_root` that was not performed,
    # and therefore an `ExpectationError` is raised.
    from some_module.some_functions import my_root

    with pytest.raises(ExpectationError):
        with Expectations():
            mock(my_root)
            Expect(my_root).to_return(3)
            assert my_root(4) == 2


def test_tear_down_keeps_permanent_mocks():
    # This test ensures that permanent mocks (i.e. those created with mock_if) are not removed by tear_down
    with Expectations():
        Expect(some_functions.my_sum).to_return(0)
        assert some_functions.my_sum(1, 2) == 0

    with pytest.raises(EnvironmentError):
        some_functions.my_sum(1, 2)
