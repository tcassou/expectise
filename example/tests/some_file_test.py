# -*- coding: utf-8 -*-
from models.some_api import SomeAPI
from nose.tools import assert_raises
from tests.my_test_case import MyTestCase

from expectise import Expect
from expectise.exceptions import EnvironmentError


class SomeFileTest(MyTestCase):
    def test_method_called(self):
        # Mocking GET API call here, without which an error would be raised,
        # as we assume GET API calls can't be processed in development / test mode
        Expect("SomeAPI").to_receive("do_something_else")
        SomeAPI.do_something_else()

    def test_some_method(self):
        # Mocking GET API call here, without which an error would be raised,
        # as we assume GET API calls can't be processed in development / test mode
        Expect("SomeAPI").to_receive("get_something").with_args("foo", "bar").and_return(False)
        assert not SomeAPI.get_something("foo", "bar")

    def test_some_other_method(self):
        # POST / DELETE API calls are mocked, and without an Expect statement they will raise an error
        assert_raises(EnvironmentError, SomeAPI.post, "foo", "bar")
