from expectise import mock_if


class SomeAPI:
    @mock_if("ENV", "test")
    @classmethod
    def do_something_else(cls, x=42):
        """Simulating a name collision with the `some_api.SomeAPI` class."""
        print(f"Doing something else with x={x}.")
        return False
