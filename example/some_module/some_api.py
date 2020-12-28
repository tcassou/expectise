# -*- coding: utf-8 -*-
from expectise import mock_if


class SomeAPI:
    @mock_if("ENV", "test")
    @classmethod
    def get_something(cls, param_1, param_2):
        print(f"Doing something with {param_1} and {param_2}")
        return True

    @mock_if("ENV", "test")
    @classmethod
    def do_something_else(cls, x=42):
        print(f"Doing something else with x={x}.")
        return False

    @mock_if("ENV", "test")
    @staticmethod
    def compute_sum(a, b):
        return a + b

    @mock_if("ENV", "test")
    def update_attribute(self, value):
        setattr(self, "my_attribute", value)
