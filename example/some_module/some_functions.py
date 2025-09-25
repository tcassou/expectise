from expectise import mock_if


@mock_if("ENV", "test")
def my_function(a: int, b: int) -> int:
    return a + b
