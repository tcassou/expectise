# -*- coding: utf-8 -*-
from unittest import TestCase

from expectise import Expect


class MyTestCase(TestCase):
    def tearDown(self):
        Expect.tear_down()
