from some_module.some_functions import my_function

from expectise import Expect
from expectise import Expectations


def test_function():
    # Everything works with functions
    with Expectations():
        Expect(my_function).to_receive(1, 2).and_return(4)
        assert my_function(1, 2) == 4
