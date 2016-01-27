"""Utilities for testing Lux applications
"""
import os
import unittest
import string
import logging
import json
from unittest import mock
from urllib.parse import urlparse, urlunparse
from io import StringIO

from pulsar import get_event_loop
from pulsar.utils.httpurl import (Headers, encode_multipart_formdata,
                                  ENCODE_BODY_METHODS)
from pulsar.utils.string import random_string
from pulsar.utils.websocket import SUPPORTED_VERSIONS, websocket_key
from pulsar.apps.wsgi import WsgiResponse
from pulsar.apps.test import test_timeout, sequential   # noqa

import lux
from lux.extensions.rest.client import LocalClient, Response
from lux.core.commands.generate_secret_key import generate_secret
logger = logging.getLogger('lux.test')


def randomname(prefix=None, len=8):
    """Generate a random name with a prefix (default to ``luxtest-``)
    """
    prefix = prefix if prefix is not None else 'luxtest-'
    name = random_string(min_len=len, max_len=len,
                         characters=string.ascii_letters)
    return ('%s%s' % (prefix, name)).lower()


def green(test_fun):
    """Decorator to run a test function in the lux application green_pool
    if available, otherwise in the event loop executor.

    In both cases it returns a :class:`~asyncio.Future`.

    This decorator should not be used for functions returning a coroutine
    or a :class:`~asyncio.Future`.
    """
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


def test_app(test, config_file=None, config_params=True, argv=None, **params):
    """Return an application for testing. Override if needed.
    """
    if config_params:
        kwargs = test.config_params.copy()
        kwargs.update(params)
        if 'SECRET_KEY' not in kwargs:
            kwargs['SECRET_KEY'] = generate_secret()
        if 'PASSWORD_SECRET_KEY' not in kwargs:
            kwargs['PASSWORD_SECRET_KEY'] = generate_secret()
    else:
        kwargs = params
    config_file = config_file or test.config_file
    if argv is None:
        argv = []
    if '--log-level' not in argv:
        argv.append('--log-level')
        levels = test.cfg.loglevel if hasattr(test, 'cfg') else ['none']
        argv.extend(levels)
    app = lux.App(config_file, argv=argv, **kwargs).setup()
    app.stdout = StringIO()
    app.stderr = StringIO()
    return app


def get_params(*names):
    cfg = {}
    for name in names:
        value = os.environ.get(name)
        if value:
            cfg[name] = value
        else:
            return
    return cfg


class TestClient:
    """An utility for simulating lux clients
    """
    def __init__(self, app, headers=None):
        self.app = app
        self.headers = headers or []

    def run_command(self, command, argv=None, **kwargs):
        argv = argv or []
        cmd = self.app.get_command(command)
        return cmd(argv, **kwargs)

    def request_start_response(self, method, path, HTTP_ACCEPT=None,
                               headers=None, body=None, content_type=None,
                               token=None, cookie=None, **extra):
        method = method.upper()
        extra['REQUEST_METHOD'] = method.upper()
        path = path or '/'
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        extra['pulsar.connection'] = mock.MagicMock()
        heads = self.headers[:]
        if headers:
            heads.extend(headers)
        if content_type:
            heads.append(('content-type', content_type))
        if token:
            heads.append(('Authorization', 'Bearer %s' % token))
        if cookie:
            heads.append(('Cookie', cookie))

        # Encode body
        if (method in ENCODE_BODY_METHODS and body and
                not isinstance(body, bytes)):
            content_type = Headers(heads).get('content-type')
            if content_type is None:
                body, content_type = encode_multipart_formdata(body)
            elif content_type == 'application/json':
                body = json.dumps(body).encode('utf-8')

        request = self.app.wsgi_request(path=path, headers=heads, body=body,
                                        extra=extra)
        start_response = mock.MagicMock()
        return request, start_response

    def request(self, method, path, **params):
        request, sr = self.request_start_response(method, path, **params)
        yield from self.app(request.environ, sr)
        return request

    def get(self, path=None, **extra):
        return self.request('get', path, **extra)

    def post(self, path=None, **extra):
        return self.request('post', path, **extra)

    def put(self, path=None, **extra):
        return self.request('put', path, **extra)

    def delete(self, path=None, **extra):
        return self.request('delete', path, **extra)

    def options(self, path=None, **extra):
        return self.request('options', path, **extra)

    def head(self, path=None, **extra):
        return self.request('head', path, **extra)

    def wsget(self, path):
        """make a websocket request"""
        headers = [('Connection', 'Upgrade'),
                   ('Upgrade', 'websocket'),
                   ('Sec-WebSocket-Version', str(max(SUPPORTED_VERSIONS))),
                   ('Sec-WebSocket-Key', websocket_key())]
        return self.get(path, headers=headers)


class TestMixin:
    config_file = 'tests.config'
    """The config file to use when building an :meth:`application`"""
    config_params = {}
    """Dictionary of parameters to override the parameters from
    :attr:`config_file`"""
    prefixdb = 'luxtest_'

    def authenticity_token(self, doc):
        name = doc.find('meta', attrs={'name': 'csrf-param'})
        value = doc.find('meta', attrs={'name': 'csrf-token'})
        if name and value:
            name = name.attrs['content']
            value = value.attrs['content']
            return {name: value}

    def cookie(self, response):
        """Extract a cookie from the response if available
        """
        headers = response.get_headers()
        return dict(headers).get('Set-Cookie')

    def bs(self, response, status_code=None, mode=None):
        """Return a BeautifulSoup object from the ``response``
        """
        from bs4 import BeautifulSoup
        return BeautifulSoup(self.html(response, status_code),
                             'html.parser')

    def html(self, response, status_code=None):
        """Get html/text content from response
        """
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.content_type,
                         'text/html; charset=utf-8')
        return self._content(response).decode('utf-8')

    def text(self, response, status_code=None):
        """Get JSON object from response
        """
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.content_type,
                         'text/plain; charset=utf-8')
        return self._content(response).decode('utf-8')

    def json(self, response, status_code=None):
        """Get JSON object from response
        """
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.content_type,
                         'application/json; charset=utf-8')
        return json.loads(self._content(response).decode('utf-8'))

    def assertValidationError(self, response, field=None, text=None):
        """Assert a Form validation error
        """
        if isinstance(response, WsgiResponse):
            self.assertEqual(response.status_code, 422)
            data = self.json(response)
        else:
            data = response
        if field is not None:
            errors = data['errors']
            self.assertTrue(errors)
            data = dict(((d.get('field', ''), d['message']) for d in errors))
            self.assertTrue(field in data)
            if text:
                self.assertEqual(data[field], text)
        elif text:
            self.assertEqual(data['message'], text)
            self.assertTrue(data['error'])

    def check_og_meta(self, bs, type=None, image=None):
        meta = bs.find('meta', property='og:type')
        self.assertEqual(meta['content'], type or 'website')
        #
        if image:
            meta = bs.find('meta', property='og:image')
            self.assertEqual(meta['content'], image)

    def _content(self, response):
        return b''.join(response.content)


class TestCase(unittest.TestCase, TestMixin):
    """TestCase class for lux tests.

    It provides several utilities methods.
    """
    apps = None

    def application(self, **params):
        """Return an application for testing. Override if needed.
        """
        app = test_app(self, **params)
        if self.apps is None:
            self.apps = []
        self.apps.append(app)
        return app

    def fetch_command(self, command, app=None):
        """Fetch a command."""
        if not app:
            app = self.application()
        cmd = app.get_command(command)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd


class AppTestCase(unittest.TestCase, TestMixin):
    """Test class for testing a single aaplication
    """
    odm = None
    """Original odm handler"""
    app = None

    @classmethod
    def setUpClass(cls):
        # Create the application
        cls.dbs = {}
        cls.app = cls.create_test_application()
        cls.client = TestClient(cls.app)
        if hasattr(cls.app, 'odm'):
            # Store the original odm for removing the new databases
            cls.odm = cls.app.odm
            return cls.setupdb()

    @classmethod
    def tearDownClass(cls):
        if cls.odm:
            return cls.dropdb()

    @classmethod
    def create_test_application(cls):
        """Return the lux application"""
        return test_app(cls)

    @classmethod
    def dbname(cls, engine):
        if engine not in cls.dbs:
            cls.dbs[engine] = randomname(cls.prefixdb)
        return cls.dbs[engine]

    @classmethod
    @green
    def setupdb(cls):
        cls.app.odm = cls.odm.database_create(database=cls.dbname)
        odm = cls.app.odm()
        DATASTORE = cls.app.config['DATASTORE']
        if not isinstance(DATASTORE, dict):
            DATASTORE = {'default': DATASTORE}
        # Replace datastores
        datastore = {}
        for original_engine, database in cls.dbs.items():
            orig_url = str(original_engine.url)
            for engine in odm.engines():
                if engine.url.database == database:
                    new_url = str(engine.url)
                    for key, url in DATASTORE.items():
                        if url == orig_url:
                            datastore[key] = new_url
        cls.app.config['DATASTORE'] = datastore
        odm.table_create()
        cls.populatedb()

    @classmethod
    @green
    def dropdb(cls):
        cls.app.odm().close()
        cls.odm().database_drop(database=cls.dbname)

    @classmethod
    def populatedb(cls):
        pass

    def create_superuser(self, username, email, password):
        """A shortcut for the create_superuser command
        """
        return self.client.run_command('create_superuser',
                                       ['--username', username,
                                        '--email', email,
                                        '--password', password])


class TestApiClient(TestClient):
    """Api client test handler
    """
    def request(self, method, path, data=None, **params):
        """Override :meth:`TestClient.request` for testing Api clients
        inside a lux application
        """
        path = urlunparse(('', '') + tuple(urlparse(path))[2:])
        params['body'] = data
        request, sr = self.request_start_response(method, path, **params)
        response = self.app(request.environ, sr)
        green_pool = self.app.green_pool
        response = green_pool.wait(response, True) if green_pool else response
        return Response(response)


class WebApiTestCase(AppTestCase):
    """Test case for an api-web application pair
    """
    web_config_file = None

    @classmethod
    def setUpClass(cls):
        assert cls.web_config_file, "no web_config_file specified"
        yield from super().setUpClass()
        cls.web = test_app(cls, config_file=cls.web_config_file,
                           config_params=False)
        api = cls.web.api
        http = api.http(cls.web)
        assert not isinstance(http, LocalClient), "API_URL not an absolute url"
        http = TestApiClient(cls.app, list(http.headers))
        api._http = http
        assert api.http(cls.web) == http
        cls.webclient = TestClient(cls.web)
