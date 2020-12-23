# -*- coding: utf-8 -*-
from expect import mock_if


class BaseAPI:
    @mock_if("ENV", "test")
    @classmethod
    def get(cls, params):
        print("Calling GET method of BaseAPI")
        return True

    @mock_if("ENV", "test")
    @classmethod
    def post(cls, params, payload):
        print("Calling POST method of BaseAPI")
        return True

    @mock_if("ENV", "test")
    @classmethod
    def delete(cls, params):
        print("Calling DELETE method of BaseAPI")
        return True
