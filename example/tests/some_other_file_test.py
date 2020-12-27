# -*- coding: utf-8 -*-
from unittest import TestCase

from models.some_api import SomeAPI

from expectise import Expect
from expectise import Expectations


class SomeOtherFileTest(TestCase):
    def test_method_called(self):
        # Using the `Expectations` context manager to make sure that the list of expectations
        # is checked in case any of them is unmet
        with Expectations():
            Expect("SomeAPI").to_receive("do_something_else")
            SomeAPI.do_something_else()
