from expectise import mock_if


@mock_if("ENV", "test")
def my_sum(a: int, b: int) -> int:
    return a + b


@mock_if("ENV", "test")
def my_square(a: int) -> int:
    return a * a


def my_root(a: int) -> int:
    return a**0.5


def my_product(a: int, b: int) -> int:
    return a * b


def my_division(a: int, b: int) -> int:
    return a / b


def my_subtraction(a: int, b: int) -> int:
    return a - b


@mock_if("ENV", "dev")
def debug():
    return "[DEBUG] This has to be a flaky operation"
