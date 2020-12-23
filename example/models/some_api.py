# -*- coding: utf-8 -*-
from example.models.base_api import BaseAPI
from expect import mock_if


class SomeAPI(BaseAPI):
    @mock_if("ENV", "test")
    @classmethod
    def get_something(cls, param_1, param_2):
        print(f"Doing something with {param_1} and {param_2}")
        return cls.get(param_1)

    @mock_if("ENV", "test")
    @classmethod
    def do_something_else(cls):
        print("Doing something else.")
        return False
