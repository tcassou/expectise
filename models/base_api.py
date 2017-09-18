# -*- coding: utf-8 -*-
from __future__ import unicode_literals

class BaseAPI:

    @classmethod
    def get(cls, params):
        print 'GET stuff'
        return True

    @classmethod
    def post(cls, params, payload):
        print 'POST stuff'
        return True

    @classmethod
    def delete(cls, params):
        print 'DELETE stuff'
        return True
