# -*- coding: utf-8 -*-
import pytest
from some_module.some_api import SomeAPI

from expectise import Expect
from expectise import Expectations
from expectise import mock
from expectise.exceptions import EnvironmentError
from expectise.exceptions import ExpectationError


"""
In this example we use the `Expectations` context manager to handle the tear down of our Expect objects.
In particular, we resolve calls to methods that were expected (in the sense of described by an `Expect` statement)
but not performed.
"""


def test_mixing_reference_modes():
    # Mixing reference modes is not allowed
    with Expectations():
        with pytest.raises(ValueError):
            Expect(SomeAPI).to_receive("get_something").with_args("foo", "bar").and_return(False)
            Expect("SomeAPI").to_receive("do_something_else").with_args(x=42).and_return(False)


def test_method():
    # The `get_something` method is mocked, and without the appropriate `Expect` statement describing its expected
    # behavior in test environment, it will raise an error.
    with pytest.raises(EnvironmentError):
        SomeAPI.get_something("foo", "bar")


def test_method_called():
    # The `do_something_else` method is mocked, an `Expect` statement is used, but it does not describe what the method
    # should perform. Therefore an exception is raised.
    with Expectations():
        Expect("SomeAPI").to_receive("do_something_else")
        with pytest.raises(EnvironmentError):
            SomeAPI.do_something_else(x=1)


def test_method_called_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("do_something_else")
        with pytest.raises(EnvironmentError):
            SomeAPI.do_something_else(x=1)


def test_method_called_with_args():
    # You can check that the correct arguments are passed to the method call. That said, for this example to work,
    # you still need to define what the mocked function should return: an `EnvironmentError` is raised.
    with Expectations():
        Expect("SomeAPI").to_receive("do_something_else").with_args(x=12)
        with pytest.raises(EnvironmentError):
            SomeAPI.do_something_else(x=12)

        # Note that in case the arguments passed do not match expectations, an `ExpectationError` is raised.
        Expect("SomeAPI").to_receive("do_something_else").with_args(x=12)
        with pytest.raises(ExpectationError):
            SomeAPI.do_something_else(x=13)


def test_method_called_with_args_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("do_something_else").with_args(x=12)
        with pytest.raises(EnvironmentError):
            SomeAPI.do_something_else(x=12)

        # Note that in case the arguments passed do not match expectations, an `ExpectationError` is raised.
        Expect(SomeAPI).to_receive("do_something_else").with_args(x=12)
        with pytest.raises(ExpectationError):
            SomeAPI.do_something_else(x=13)


def test_method_return():
    # Expecting the function `get_something` to be called, with specifc arguments passed to it, and overriding its
    # behavior to return a desired output. This test case checks that the method is called, with the right input,
    # and modifies its return value(s). Can be useful in case the `get_something` performs a call to an external
    # service that you want to avoid in test environment, and therefore want to mock the response with your output.
    with Expectations():
        Expect("SomeAPI").to_receive("get_something").with_args("foo", "bar").and_return(False)
        # This example is silly of course. Instead, some more complex logic in your module would trigger the call
        # to `get_something` with the specific input you expect. Here, we mock the output with a `return False`.
        assert not SomeAPI.get_something("foo", "bar")


def test_method_return_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("get_something").with_args("foo", "bar").and_return(False)
        assert not SomeAPI.get_something("foo", "bar")


def test_method_called_twice():
    # With the same setup as above, calling the same method a second time will raise an error. 2 `Expect`
    # statements are required for that.
    with Expectations():
        Expect("SomeAPI").to_receive("get_something").with_args("foo", "bar").and_return(False)
        SomeAPI.get_something("foo", "bar")
        with pytest.raises(ExpectationError):
            SomeAPI.get_something("foo", "bar")


def test_method_called_twice_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("get_something").with_args("foo", "bar").and_return(False)
        SomeAPI.get_something("foo", "bar")
        with pytest.raises(ExpectationError):
            SomeAPI.get_something("foo", "bar")


def test_method_raise():
    # Expecting the function `get_something` to be called, with specifc arguments passed to it, and overriding its
    # behavior to raise the desired error. This test case checks that the method is called, with the right input,
    # and modifies its behavior. Can be useful to ensure that your code handles exceptions gracefully.
    with Expectations():
        Expect("SomeAPI").to_receive("get_something").with_args("foo", "bar").and_raise(ValueError("My error"))
        # Again, silly example, just to illustrate what can be done with the framework.
        with pytest.raises(ValueError):
            SomeAPI.get_something("foo", "bar")


def test_method_raise_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("get_something").with_args("foo", "bar").and_raise(ValueError("My error"))
        with pytest.raises(ValueError):
            SomeAPI.get_something("foo", "bar")


def test_method_return_only():
    # Similar example as above, with no check of arguments passed to `get_something`.
    with Expectations():
        Expect("SomeAPI").to_receive("get_something").and_return(42)
        assert SomeAPI.get_something("foo", "bar") == 42


def test_method_return_only_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("get_something").and_return(42)
        assert SomeAPI.get_something("foo", "bar") == 42


def test_method_raise_only():
    # Similar example as above, with no check of arguments passed to `get_something`.
    with Expectations():
        Expect("SomeAPI").to_receive("get_something").and_raise(ValueError("My error"))
        with pytest.raises(ValueError):
            SomeAPI.get_something("python", "snake")


def test_method_raise_only_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("get_something").and_raise(ValueError("My error"))
        with pytest.raises(ValueError):
            SomeAPI.get_something("python", "snake")


def test_static_method():
    # Everything works with staticmethods defined
    with Expectations():
        Expect("SomeAPI").to_receive("compute_sum").with_args(1, 2).and_return(4)
        assert SomeAPI.compute_sum(1, 2) == 4


def test_static_method_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("compute_sum").with_args(1, 2).and_return(4)
        assert SomeAPI.compute_sum(1, 2) == 4


def test_instance_method():
    # Everything works with instance methods
    with Expectations():
        Expect("SomeAPI").to_receive("update_attribute").and_return("sshhhh")
        assert SomeAPI().update_attribute("secret_value") == "sshhhh"


def test_instance_method_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("update_attribute").and_return("sshhhh")
        assert SomeAPI().update_attribute("secret_value") == "sshhhh"


def test_property():
    # Everything works with properties
    with Expectations():
        Expect("SomeAPI").to_receive("some_property").and_return("bar")
        assert SomeAPI().some_property == "bar"


def test_property_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        Expect(SomeAPI).to_receive("some_property").and_return("bar")
        assert SomeAPI().some_property == "bar"


def test_disable():
    # Trying to disable a mock
    with Expectations():
        some_api = SomeAPI()

        # Disabling the mock should allow setting the property
        Expect.disable_mock("SomeAPI", "update_attribute")
        some_api.update_attribute("new_value")
        assert some_api.my_attribute == "new_value"


def test_disable_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        some_api = SomeAPI()
        Expect.disable_mock(SomeAPI, "update_attribute")
        some_api.update_attribute("new_value")
        assert some_api.my_attribute == "new_value"


def test_tear_down_disables_temporary_mocks():
    # This test ensures that calling mock(...) and then
    # tearing down (by exiting the context manager)
    # fully removes the Mock and does not impact future tests
    with Expectations():
        some_api = SomeAPI()
        mock(SomeAPI, SomeAPI.unmocked_method, "ENV", "test")
        Expect("SomeAPI").to_receive("unmocked_method").and_return("mocked")

        assert some_api.unmocked_method() == "mocked"

    assert some_api.unmocked_method() == "unmocked"


def test_tear_down_disables_temporary_mocks_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        some_api = SomeAPI()
        mock(SomeAPI, SomeAPI.unmocked_method, "ENV", "test")
        Expect(SomeAPI).to_receive("unmocked_method").and_return("mocked")

        assert some_api.unmocked_method() == "mocked"

    assert some_api.unmocked_method() == "unmocked"


def test_tear_down_keeps_permanent_mocks():
    # This test ensures that permanent mocks (i.e. those
    # created with mock_if - wen in the test environment)
    # are not removed by tear_down
    with Expectations():
        some_api = SomeAPI()

        Expect("SomeAPI").to_receive("mocked_method").and_return("mocked")

        assert some_api.mocked_method() == "mocked"

    with pytest.raises(EnvironmentError):
        some_api.mocked_method()


def test_tear_down_keeps_permanent_mocks_by_class():
    # Same test as above, but using the class itself instead of the class name as a reference.
    with Expectations():
        some_api = SomeAPI()
        Expect(SomeAPI).to_receive("mocked_method").and_return("mocked")
        assert some_api.mocked_method() == "mocked"

    with pytest.raises(EnvironmentError):
        some_api.mocked_method()
