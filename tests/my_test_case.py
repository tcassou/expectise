# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from unittest import TestCase

from models.base_api import BaseAPI
from tests.expect import Expect
from tests.expect import models


def override_api():
    """ Overriding all models. """
    def raise_api_call(*args, **kwargs):
        raise Exception('Get API calls not allowed in test environment')

    def inactive_api_call(*args, **kwargs):
        pass

    setattr(BaseAPI, 'get', classmethod(raise_api_call))
    for method_name in ['post', 'delete']:
        setattr(BaseAPI, method_name, classmethod(inactive_api_call))


def reset_api():
    """Resetting methods that were overruled during unit tests"""
    for (klass, method), args in Expect.method_h.iteritems():
        setattr(models[klass], method, args['method'])


def assert_decorated_methods():
    for (klass, method), args in Expect.method_h.iteritems():
        remain = args['expected'] - args['performed']
        if remain > 0:
            Expect.method_h = {}
            assert 0, '{} method of class {} still expected to be called {} time(s).'.format(method, klass, remain)
    Expect.method_h = {}


class MyTestCase(TestCase):

    def setUp(self):
        override_api()

    def tearDown(self):
        reset_api()
        assert_decorated_methods()
