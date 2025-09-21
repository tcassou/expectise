from some_module.some_conflicting_api import SomeAPI

from expectise import Expect
from expectise import Expectations


"""
In this example, we show how to handle potential collisions between class names, by creating mocks that
reference the class itself instead of the class name.
Using class names as references is a handy shortcut when there are no collisions, as it may save a lot of
import statements, but it only works if there are no collisions.
"""


def test_collision():
    # some_module.some_conflicting_api defines a class named `SomeAPI`, which name collides
    # with the `SomeAPI` class from some_module.some_api.
    # This class name collision has no impact on the test, as the mock references the class itself.
    with Expectations():
        Expect(SomeAPI).to_receive("do_something_else").with_args(x=42).and_return(12)
        assert SomeAPI.do_something_else(x=42) == 12
