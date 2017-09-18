# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from models.base_api import BaseAPI


class SomeAPI(BaseAPI):

    @classmethod
    def get_some_stuff(cls, param_1, param_2):
        print 'doing some stuff with {} and {}'.format(param_1, param_2)
        print 'GET some stuff'
        return cls.get(param_1)
