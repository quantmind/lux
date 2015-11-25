from urllib.parse import urlparse

from pulsar.apps.wsgi.utils import query_dict

from lux.utils import test
from lux.extensions.rest import Pagination


class TestUtils(test.TestCase):
    config_file = 'tests.rest'

    def test_last_link(self):
        app = self.application()
        request = app.wsgi_request()
        pagination = Pagination()
        #
        pag = pagination(request, [], 120, 25, 0)
        query = query_dict(urlparse(pag['next']).query)
        self.assertEqual(query['offset'], '25')
        query = query_dict(urlparse(pag['last']).query)
        self.assertEqual(query['offset'], '100')
        #
        pag = pagination(request, [], 120, 25, 75)
        query = query_dict(urlparse(pag['last']).query)
        self.assertEqual(query['offset'], '100')
        self.assertFalse('next' in pag)
        #
        pag = pagination(request, [], 120, 25, 50)
        query = query_dict(urlparse(pag['next']).query)
        self.assertEqual(query['offset'], '75')
        query = query_dict(urlparse(pag['last']).query)
        self.assertEqual(query['offset'], '100')

    def test_custom_offset(self):
        app = self.application()
        request = app.wsgi_request()
        pagination = Pagination()
        #
        pag = pagination(request, [], 27, 5, 2)
        self.assertFalse('prev' in pag)
        query = query_dict(urlparse(pag['first']).query)
        self.assertEqual(query['offset'], '0')
        self.assertEqual(query['limit'], '2')
        query = query_dict(urlparse(pag['last']).query)
        self.assertEqual(query['offset'], '22')
        self.assertEqual(query['limit'], '5')
        #
        pag = pagination(request, [], 27, 5, 22)
        self.assertFalse('next' in pag)
        self.assertFalse('last' in pag)
        query = query_dict(urlparse(pag['first']).query)
        self.assertEqual(query['offset'], '0')
        self.assertEqual(query['limit'], '2')
        query = query_dict(urlparse(pag['prev']).query)
        self.assertEqual(query['offset'], '17')
        self.assertEqual(query['limit'], '5')
