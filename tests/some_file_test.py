# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tests.expect import Expect
from tests.my_test_case import MyTestCase

from models.some_api import SomeAPI


class SomeFileTest(MyTestCase):

    def test_some_method(self):
        # Mocking GET API call here, withou which an error would be raised,
        # as we assume GET calls can't be processed in development / test mode
        Expect('SomeAPI')\
            .to_receive('get_some_stuff')\
            .with_args('foo', 'bar')\
            .and_return(False)
        assert not SomeAPI.get_some_stuff('foo', 'bar')

    def test_some_other_method(self):
        # POST / DELETE API calls are mocked, which is why the following POST call returns None
        assert SomeAPI.post('foo', 'bar') is None
