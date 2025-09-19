# -*- coding: utf-8 -*-
import pytest
from some_module.some_conflicting_api import SomeAPI

from expectise import Expect
from expectise import Expectations
from expectise.exceptions import EnvironmentError


"""
In this example, we show how to handle potential collisions between class names, by creating mocks that
reference the class itself instead of the class name.
Using class names as references is a handy shortcut when there are no collisions, as it may save a lot of
import statements, but it only works if there are no collisions.
"""


def test_collision_by_class():
    # some_module.some_conflicting_api defines a class named `SomeAPI` that collides with the
    # `SomeAPI` class from some_module.some_api.
    # Creating a mock that references the class itself leaves no room for ambiguity, and the test behaves as expected.
    with Expectations():
        Expect(SomeAPI).to_receive("do_something_else").with_args(x=42).and_return(12)
        assert SomeAPI.do_something_else(x=42) == 12


def test_collision():
    # Creating a mock that references the class name leaves room for ambiguity, and in this case, due to the same
    # key being overridden under the hood, only the `SomeAPI` class from some_module.some_api is mocked,
    # and not the `SomeAPI` class from some_module.some_conflicting_api.
    # As a result, an `EnvironmentError` is raised, suggesting to mock the right class and method before using it.
    with pytest.raises(EnvironmentError):
        with Expectations():
            Expect("SomeAPI").to_receive("do_something_else").with_args(x=42).and_return(12)
            assert SomeAPI.do_something_else(x=42) == 12
