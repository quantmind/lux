"""Utilities for testing Lux applications"""
import os
import unittest
import string
import logging
import json as _json
import pickle
from collections import OrderedDict
from unittest import mock
from io import StringIO

from pulsar import get_event_loop, as_coroutine
from pulsar.utils.httpurl import (Headers, encode_multipart_formdata,
                                  ENCODE_BODY_METHODS, remove_double_slash,
                                  parse_options_header)
from pulsar.utils.string import random_string
from pulsar.utils.websocket import (SUPPORTED_VERSIONS, websocket_key,
                                    frame_parser)
from pulsar.apps.wsgi import WsgiResponse
from pulsar.apps.http import JSON_CONTENT_TYPES
from pulsar.apps.test import test_timeout, sequential

from lux.core import App
from lux.extensions.rest import ApiClient
from lux.core.commands.generate_secret_key import generate_secret

logger = logging.getLogger('pulsar.test')


__all__ = ['TestClient',
           'TestCase',
           'AppTestCase',
           'WebApiTestCase',
           'load_fixtures',
           'randomname',
           'green',
           'sequential',
           'test_timeout']


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

    This decorator should not be used for functions returning an
    awaitable.
    """
    def _(*args, **kwargs):
        assert len(args) >= 1, ("green decorator should be applied to test "
                                "functions only")
        try:
            pool = args[0].app.green_pool
        except AttributeError:
            pool = None
        if pool:
            return pool.submit(test_fun, *args, **kwargs)
        else:
            loop = get_event_loop()
            return loop.run_in_executor(None, test_fun, *args, **kwargs)

    return _


def test_app(test, config_file=None, config_params=True, argv=None,
             api_app=None, **params):
    """Return an application for testing. Override if needed.
    """
    if config_params:
        kwargs = test.config_params.copy()
        kwargs.update(params)
        if 'SECRET_KEY' not in kwargs:
            kwargs['SECRET_KEY'] = generate_secret()
    else:
        kwargs = params
    config_file = config_file or test.config_file
    if argv is None:
        argv = []
    if '--log-level' not in argv:
        argv.append('--log-level')
        levels = test.cfg.log_level if hasattr(test, 'cfg') else ['none']
        argv.extend(levels)
    app = App(config_file, argv=argv, **kwargs).setup(
        on_config=test.app_test_providers)
    app.stdout = StringIO()
    app.stderr = StringIO()
    return app


@green
def create_users(app, items):
    items.insert(0, {
        "username": "testuser",
        "password": "testuser",
        "superuser": True,
        "active": True
    })
    logger.debug('Creating %d users', len(items))
    request = app.wsgi_request()
    auth = app.auth_backend
    processed = set()
    for params in items:
        if params.get('username') in processed:
            continue
        user = auth.create_user(request, **params)
        processed.add(user.username)
    return len(processed)


async def load_fixtures(app, path=None):
    if not hasattr(app.auth_backend, 'create_user'):
        return

    fpath = path if path else os.path.join(app.meta.path, 'fixtures')

    fixtures = OrderedDict()
    if os.path.isdir(fpath):
        for filename in os.listdir(fpath):
            if filename.endswith('.json'):
                with open(os.path.join(fpath, filename), 'r') as file:
                    fixtures.update(_json.load(file,
                                               object_pairs_hook=OrderedDict))
    else:
        if path:
            logger.error('Could not find %s path for fixtures', path)
        return 0

    total = await create_users(app, fixtures.pop('users', []))

    client = TestClient(app)
    test = TestCase()
    test_tokens = {}

    for model, items in fixtures.items():
        logger.info('Creating %d fixtures for "%s"', len(items), model)
        for params in items:
            url = params.pop('api_url', '/%s' % model)
            user = params.pop('api_user', 'testuser')
            if user not in test_tokens:
                request = await client.post('/authorizations',
                                            json=dict(username=user,
                                                      password=user))
                token = test.json(request.response, 201)['token']
                test_tokens[user] = token
            test_token = test_tokens[user]
            request = await client.post(url,
                                        json=params,
                                        token=test_token)
            data = test.json(request.response)
            code = request.response.status_code
            if code > 201:
                raise AssertionError('%s api call got %d: %s' %
                                     (url, code, data))
            total += 1

    logger.info('Created %s objects from %d models', total, 1 + len(fixtures))


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
                               headers=None, body=None, json=None,
                               content_type=None, token=None, cookie=None,
                               **extra):
        method = method.upper()
        extra['REQUEST_METHOD'] = method.upper()
        path = path or '/'
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        extra['pulsar.connection'] = mock.MagicMock()
        heads = self.headers[:]
        if headers:
            heads.extend(headers)
        if json is not None:
            content_type = 'application/json'
            assert not body
            body = json
        if content_type:
            heads.append(('content-type', content_type))
        if token:
            heads.append(('Authorization', 'Bearer %s' % token))
        if cookie:
            heads.append(('Cookie', cookie))

        # Encode body
        if (method in ENCODE_BODY_METHODS and body is not None and
                not isinstance(body, bytes)):
            content_type = Headers(heads).get('content-type')
            if content_type is None:
                body, content_type = encode_multipart_formdata(body)
                heads.append(('content-type', content_type))
            elif content_type == 'application/json':
                body = _json.dumps(body).encode('utf-8')

        request = self.app.wsgi_request(path=path, headers=heads, body=body,
                                        **extra)
        request.environ['SERVER_NAME'] = 'localhost'
        start_response = mock.MagicMock()
        return request, start_response

    async def request(self, method, path, **params):
        request, sr = self.request_start_response(method, path, **params)
        await self.app(request.environ, sr)
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


class TestHttpApiClient(TestClient):
    """Api client test handler
    """
    def request(self, method, path, data=None, **params):
        """Override :meth:`TestClient.request` for testing Api clients
        inside a lux application
        """
        params['body'] = data
        request, sr = self.request_start_response(method, path, **params)
        response = self.app(request.environ, sr)
        green_pool = self.app.green_pool
        response = green_pool.wait(response, True) if green_pool else response
        return Response(response)


class TestMixin:
    app = None
    """Test class application"""
    config_file = 'tests.config'
    """The config file to use when building an :meth:`application`"""
    config_params = {}
    """Dictionary of parameters to override the parameters from
    :attr:`config_file`"""
    prefixdb = 'luxtest_'

    @classmethod
    def app_test_providers(cls, app):
        if 'Api' in app.providers:
            app.providers['Api'] = cls.apiClient

    @classmethod
    def apiClient(cls, app):
        api = ApiClient(app)
        api.http = TestHttpApiClient(cls.app or app)
        return api

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
        return _json.loads(self._content(response).decode('utf-8'))

    def xml(self, response, status_code=None):
        """Get JSON object from response
        """
        from bs4 import BeautifulSoup
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.content_type,
                         'application/xml; charset=utf-8')
        text = self._content(response).decode('utf-8')
        return BeautifulSoup(text, 'xml')

    def ws_upgrade(self, response):
        from lux.extensions.sockjs import LuxWs
        self.assertEqual(response.status_code, 101)
        #
        connection = response.connection
        upgrade = connection.upgrade
        self.assertTrue(upgrade.called)
        websocket = upgrade.call_args[0][0](get_event_loop())
        connection.reset_mock()
        #
        self.assertIsInstance(websocket.handler, LuxWs)
        websocket._connection = response.connection
        websocket.connection_made(response.connection)
        self.assertTrue(websocket.cache.wsclient)
        websocket.cache.wsclient.logger = mock.MagicMock()
        return websocket

    def ws_message(self, **params):
        msg = _json.dumps(params)
        return _json.dumps([msg])

    def get_ws_message(self, websocket):
        mock = websocket.connection.write
        self.assertTrue(mock.called)
        frame = mock.call_args[0][0]
        return self.parse_frame(websocket, frame)

    def parse_frame(self, websocket, frame):
        parser = frame_parser(kind=1)
        frame = parser.decode(frame)
        wsclient = websocket.cache.wsclient
        websocket.connection.reset_mock()
        msg = _json.loads(frame.body[1:])[0]
        return wsclient.protocol.decode(msg)

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

    def check401(self, response):
        self.json(response, 401)
        self.assertEqual(response.headers['WWW-Authenticate'], 'Token')

    def checkOptions(self, response, methods=None):
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Access-Control-Allow-Origin' in response.headers)
        methods_header = response.headers['Access-Control-Allow-Methods']
        headers = set(methods_header.split(', '))
        if methods:
            self.assertEqual(set(methods), headers)

    def check_og_meta(self, bs, type=None, image=None):
        meta = bs.find('meta', property='og:type')
        self.assertEqual(meta['content'], type or 'website')
        #
        if image:
            meta = bs.find('meta', property='og:image')
            self.assertEqual(meta['content'], image)

    def get_command(self, app, command):
        cmd = app.get_command(command)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        self.assertTrue(cmd.help)
        return cmd

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

    def fetch_command(self, command, app=None, **params):
        """Fetch a command."""
        if not app:
            app = self.application(**params)
        return self.get_command(app, command)


class AppTestCase(unittest.TestCase, TestMixin):
    """Test class for testing a single application
    """
    odm = None
    """Original odm handler"""
    datastore = None
    """Test class datastore dictionary"""

    @classmethod
    async def setUpClass(cls):
        # Create the application
        cls.dbs = {}
        cls.app = cls.create_test_application()
        cls.client = cls.get_client()
        if hasattr(cls.app, 'odm'):
            # Store the original odm for removing the new databases
            cls.odm = cls.app.odm
            await cls.setupdb()
        await as_coroutine(cls.populatedb())
        await as_coroutine(cls.beforeAll())

    @classmethod
    def tearDownClass(cls):
        if cls.odm:
            return cls.dropdb()

    @classmethod
    def get_client(cls):
        return TestClient(cls.app)

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
        #
        # Replace datastores with temporary ones for this test class
        cls.datastore = {}
        for original_engine, database in cls.dbs.items():
            orig_url = str(original_engine.url)
            for engine in odm.engines():
                if engine.url.database == database:
                    new_url = str(engine.url)
                    for key, url in DATASTORE.items():
                        if url == orig_url:
                            cls.datastore[key] = new_url
        cls.app.config['DATASTORE'] = cls.datastore
        odm.table_create()

    @classmethod
    @green
    def dropdb(cls):
        cls.app.odm().close()
        cls.odm().database_drop(database=cls.dbname)

    @classmethod
    def populatedb(cls):
        return load_fixtures(cls.app)

    @classmethod
    def api_url(cls, path):
        return remove_double_slash('%s/%s' % (cls.app.config['API_URL'], path))

    @classmethod
    def clone_app(cls):
        sapp = pickle.dumps(cls.app.callable)
        app = pickle.loads(sapp).setup(handler=False)
        if cls.datastore:
            app.config['DATASTORE'] = cls.datastore
        return TestApp(app)

    @classmethod
    def beforeAll(cls):
        """Can be used to add logic before all tests"""

    def fetch_command(self, command, new=False):
        """Fetch a command."""
        app = self.app
        if new:
            app = self.clone_app()
        return self.get_command(app, command)

    def create_superuser(self, username, email, password):
        """A shortcut for the create_superuser command
        """
        return self.client.run_command('create_superuser',
                                       ['--username', username,
                                        '--email', email,
                                        '--password', password])

    async def _token(self, credentials):
        '''Return a token for a user
        '''
        if isinstance(credentials, str):
            credentials = {"username": credentials,
                           "password": credentials}

        # Get new token
        request = await self.client.post('/authorizations',
                                         json=credentials)
        user = request.cache.user
        self.assertFalse(user.is_authenticated())
        data = self.json(request.response, 201)
        self.assertTrue('token' in data)
        return data['token']


class WebApiTestCase(AppTestCase):
    """Test case for an api-web application pair
    """
    web_config_file = None

    @classmethod
    async def setUpClass(cls):
        assert cls.web_config_file, "no web_config_file specified"
        await as_coroutine(super().setUpClass())
        cls.web = test_app(cls, config_file=cls.web_config_file,
                           config_params=False, api_app=cls.app)
        assert cls.web.api.http.app is cls.app
        cls.webclient = TestClient(cls.web)

    def check_html_token(self, doc, token):
        value = doc.find('meta', attrs={'name': 'user-token'})
        if value:
            self.assertEqual(value.attrs['content'], token)
        else:
            raise ValueError('user-token meta tag not available')

    async def _cookie_csrf(self, url, csrf=None, cookie=None):
        # We need csrf and cookie to post data to the web site
        if csrf is None:
            request = await self.webclient.get(url, cookie=cookie)
            bs = self.bs(request.response, 200)
            csrf = self.authenticity_token(bs)
            if not cookie:
                cookie = self.cookie(request.response)
        return cookie, csrf or {}

    async def _signup(self, csrf=None):
        """Signup to the web site
        """
        url = self.app.config['REGISTER_URL']
        cookie, csrf = await self._cookie_csrf(url, csrf)
        username = randomname(prefix='u-')
        password = randomname()
        email = '%s@%s.com' % (username, randomname())
        data = {'username': username,
                'password': password,
                'password_repeat': password,
                'email': email}
        data.update(csrf)
        request = await self.webclient.post(url,
                                            body=data,
                                            cookie=cookie,
                                            content_type='application/json')
        return self.json(request.response, 201)

    @green
    def _get_registration(self, email):
        """Retrieve the registration object from email

        Useful for testing signup process
        """
        odm = self.app.odm()
        with odm.begin() as session:
            query = session.query(odm.registration).join(odm.user).filter(
                odm.user.email == email)
            return query.one()


class Response:
    __slots__ = ('response',)

    def __init__(self, response):
        self.response = response

    def _repr__(self):
        return repr(self.response)

    def __getattr__(self, name):
        return getattr(self.response, name)

    @property
    def content(self):
        '''Retrieve the body without flushing'''
        return b''.join(self.response.content)

    def text(self, charset=None, errors=None):
        charset = charset or self.response.encoding or 'utf-8'
        return self.content.decode(charset, errors or 'strict')

    def json(self, charset=None, errors=None):
        return _json.loads(self.text(charset, errors))

    def decode_content(self):
        '''Return the best possible representation of the response body.
        '''
        ct = self.response.content_type
        if ct:
            ct, _ = parse_options_header(ct)
            if ct in JSON_CONTENT_TYPES:
                return self.json()
            elif ct.startswith('text/'):
                return self.text()
        return self.content


class TestApp:

    def __init__(self, app):
        self.app = app
        app.stdout = StringIO()
        app.stderr = StringIO()

    def __getattr__(self, name):
        return getattr(self.app, name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        odm = self.odm
        if odm:
            odm.close()
