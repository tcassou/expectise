# -*- coding: utf-8 -*-
from unittest import TestCase

from expector import Expect


class MyTestCase(TestCase):
    def tearDown(self):
        Expect.tear_down()
