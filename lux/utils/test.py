'''Utilities for testing Lux applications
'''
import unittest
import string
import logging
import json
from unittest import mock
from io import StringIO

from pulsar import get_event_loop
from pulsar.utils.httpurl import encode_multipart_formdata
from pulsar.utils.string import random_string
from pulsar.apps.test import test_timeout   # noqa

import lux
from lux.core.commands.generate_secret_key import generate_secret

logger = logging.getLogger('lux.test')


def randomname(prefix=None):
    '''Generate a random name with a prefix (default to ``luxtest_``)
    '''
    prefix = prefix or 'luxtest_'
    name = random_string(min_len=8, max_len=8, characters=string.ascii_letters)
    return ('%s%s' % (prefix, name)).lower()


def green(test_fun):
    '''Decorator to run a test function in the lux application green_pool
    if available, otherwise in the event loop executor.

    In both cases it returns a :class:`~asyncio.Future`.

    This decorator should not be used for functions returning a coroutine
    or a :class:`~asyncio.Future`.
    '''
    def _(o):
        try:
            pool = o.app.green_pool
        except AttributeError:
            pool = None
        if pool:
            return pool.submit(test_fun, o)
        else:
            loop = get_event_loop()
            return loop.run_in_executor(None, test_fun, o)

    return _


def test_app(test, config_file=None, argv=None, **params):
    '''Return an application for testing. Override if needed.
    '''
    kwargs = test.config_params.copy()
    kwargs.update(params)
    if 'SECRET_KEY' not in kwargs:
        kwargs['SECRET_KEY'] = generate_secret()
    config_file = config_file or test.config_file
    if argv is None:
        argv = []
    if '--log-level' not in argv:
        argv.append('--log-level')
        levels = test.cfg.loglevel if hasattr(test, 'cfg') else ['none']
        argv.extend(levels)

    app = lux.App(config_file, argv=argv, **kwargs).setup()
    #
    # Data mapper
    app.stdout = StringIO()
    app.stderr = StringIO()
    return app


class TestClient:
    '''An utility for simulating lux clients
    '''
    def __init__(self, app):
        self.app = app

    def run_command(self, command, argv=None, **kwargs):
        argv = argv or []
        cmd = self.app.get_command(command)
        return cmd(argv, **kwargs)

    def request_start_response(self, path=None, HTTP_ACCEPT=None,
                               headers=None, body=None, content_type=None,
                               token=None, cookie=None, **extra):
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        headers = headers or []
        if content_type:
            headers.append(('content-type', content_type))
        if token:
            headers.append(('Authorization', 'Bearer %s' % token))
        if cookie:
            headers.append(('Cookie', cookie))
        request = self.app.wsgi_request(path=path, headers=headers, body=body,
                                        extra=extra)
        start_response = mock.MagicMock()
        return request, start_response

    def request(self, **params):
        request, sr = self.request_start_response(**params)
        yield from self.app(request.environ, sr)
        return request

    def get(self, path=None, **extra):
        extra['REQUEST_METHOD'] = 'GET'
        return self.request(path=path, **extra)

    def post(self, path=None, body=None, content_type=None, **extra):
        extra['REQUEST_METHOD'] = 'POST'
        if body is not None and not isinstance(body, bytes):
            if content_type is None:
                body, content_type = encode_multipart_formdata(body)
            elif content_type == 'application/json':
                body = json.dumps(body).encode('utf-8')

        return self.request(path=path, content_type=content_type,
                            body=body, **extra)

    def delete(self, path=None, **extra):
        extra['REQUEST_METHOD'] = 'DELETE'
        return self.request(path=path, **extra)

    def options(self, path=None, **extra):
        extra['REQUEST_METHOD'] = 'OPTIONS'
        return self.request(path=path, **extra)


class TestMixin:
    config_file = 'tests.config'
    '''The config file to use when building an :meth:`application`'''
    config_params = {}
    '''Dictionary of parameters to override the parameters from
    :attr:`config_file`'''
    prefixdb = 'luxtest_'

    def authenticity_token(self, doc):
        name = doc.find('meta', attrs={'name': 'csrf-param'})
        value = doc.find('meta', attrs={'name': 'csrf-token'})
        if name and value:
            name = name.attrs['content']
            value = value.attrs['content']
            return {name: value}

    def cookie(self, response):
        '''Extract a cookie from the response if available
        '''
        headers = response.get_headers()
        return dict(headers).get('Set-Cookie')

    def bs(self, response):
        '''Return a BeautifulSoup object from the ``response``
        '''
        from bs4 import BeautifulSoup
        return BeautifulSoup(self.html(response))

    def html(self, response):
        '''Get html/text content from response
        '''
        self.assertEqual(response.content_type,
                         'text/html; charset=utf-8')
        return response.content[0].decode('utf-8')

    def json(self, response):
        '''Get JSON object from response
        '''
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')
        return json.loads(response.content[0].decode('utf-8'))


class TestCase(unittest.TestCase, TestMixin):
    '''TestCase class for lux tests.

    It provides several utilities methods.
    '''
    apps = None

    def application(self, **params):
        '''Return an application for testing. Override if needed.
        '''
        app = test_app(self, **params)
        if self.apps is None:
            self.apps = []
        self.apps.append(app)
        return app

    def request_start_response(self, app, path=None, HTTP_ACCEPT=None,
                               headers=None, body=None, **extra):
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        request = app.wsgi_request(path=path, headers=headers, body=body,
                                   extra=extra)
        start_response = mock.MagicMock()
        return request, start_response

    def fetch_command(self, command, app=None):
        '''Fetch a command.'''
        if not app:
            app = self.application()
        cmd = app.get_command(command)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd


class AppTestCase(unittest.TestCase, TestMixin):
    '''Test calss for testing applications
    '''
    odm = None
    app = None

    @classmethod
    def setUpClass(cls):
        # Create the application
        cls.dbs = {}
        cls.app = test_app(cls)
        cls.client = TestClient(cls.app)
        if hasattr(cls.app, 'odm'):
            cls.odm = cls.app.odm
            return cls.setupdb()

    @classmethod
    def tearDownClass(cls):
        if cls.odm:
            return cls.dropdb()

    @classmethod
    def dbname(cls, engine):
        if engine not in cls.dbs:
            cls.dbs[engine] = randomname(cls.prefixdb)
        return cls.dbs[engine]

    @classmethod
    @green
    def setupdb(cls):
        cls.app.odm = cls.odm.database_create(database=cls.dbname)
        logger.info('Create test tables')
        cls.app.odm().table_create()
        cls.populatedb()

    @classmethod
    @green
    def dropdb(cls):
        logger.info('Drop databases')
        cls.app.odm().close()
        cls.odm().database_drop(database=cls.dbname)

    @classmethod
    def populatedb(cls):
        pass

    def create_superuser(self, username, email, password):
        '''A shortcut for the create_superuser command
        '''
        return self.client.run_command('create_superuser',
                                       ['--username', username,
                                        '--email', email,
                                        '--password', password])
