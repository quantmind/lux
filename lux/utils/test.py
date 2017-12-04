"""Utilities for testing Lux applications"""
import os
import unittest
import string
import logging
import pickle
from asyncio import get_event_loop
from collections import OrderedDict
from unittest import mock
from io import StringIO

from pulsar.api import as_coroutine
from pulsar.utils.httpurl import remove_double_slash
from pulsar.utils.string import random_string
from pulsar.utils.websocket import frame_parser
from pulsar.apps.wsgi import WsgiResponse
from pulsar.utils.system import json as _json
from pulsar.apps.test import test_timeout, sequential, test_wsgi_request
from pulsar.apps.greenio import wait, run_in_greenlet

from lux.core import App, AppClient
from lux.core.commands.generate_secret_key import generate_secret
from lux.utils import context

from .token import app_token


logger = logging.getLogger('pulsar.test')


__all__ = ['TestCase',
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


def wsgi_request_from_app(app, **kw):
    request = wait(test_wsgi_request(**kw))
    app.on_request(request)
    return request


def green(test_fun):
    """Decorator to run a test function in the lux application green_pool
    if available, otherwise in the event loop executor.

    In both cases it returns a :class:`~asyncio.Future`.

    This decorator should not be used for functions returning an
    awaitable.
    """
    @run_in_greenlet
    def _(test):
        context.set_app(getattr(test, 'app', None))
        return test_fun(test)

    return _


def test_app(test, config_file=None, config_params=True, argv=None, **params):
    """Return an application for testing. Override if needed.
    """
    if config_params:
        kwargs = test.config_params.copy()
        kwargs.update(params)
    else:
        kwargs = params
    config_file = config_file or test.config_file
    if argv is None:
        argv = []
    if '--log-level' not in argv:
        argv.append('--log-level')
        levels = test.cfg.log_level if hasattr(test, 'cfg') else ['none']
        argv.extend(levels)
    app = App(config_file, argv=argv, cfg=test.cfg, **kwargs).setup()
    if app.config['SECRET_KEY'] == 'secret-key':
        app.config['SECRET_KEY'] = generate_secret()
    app.stdout = StringIO()
    app.stderr = StringIO()
    assert app.request_handler()
    return app


@green
def create_users(app, items, testuser, index=None):
    if not index:
        items.insert(0, {
            "username": testuser,
            "password": testuser,
            "superuser": True,
            "active": True
        })
    logger.debug('Creating %d users', len(items))
    request = wsgi_request_from_app(app)
    processed = set()
    with app.models['users'].session(request) as session:
        for params in items:
            if params.get('username') in processed:
                continue
            user = session.auth.create_user(session, **params)
            if user:
                processed.add(user.username)
    return len(processed)


async def load_fixtures(app, path=None, api_url=None, testuser=None,
                        admin_jwt=None):
    """Load fixtures

    This function requires an authentication backend supporting user creation
    """
    testuser = testuser or 'testuser'
    fpath = path if path else os.path.join(app.meta.path, 'fixtures')
    total = 0

    if not os.path.isdir(fpath):
        if path:
            logger.error('Could not find %s path for fixtures', path)
        return total

    api_url = api_url or ''
    if api_url.endswith('/'):
        api_url = api_url[:-1]

    client = AppClient.create(app, False)
    test = TestCase()
    test_tokens = {}

    for index, fixtures in enumerate(_read_fixtures(fpath)):

        total += await create_users(
            app, fixtures.pop('users', []), testuser, index
        )

        for name, items in fixtures.items():
            logger.info('%d fixtures for "%s"', len(items), name)
            for params in items:
                user = params.pop('api_user', testuser)
                if user not in test_tokens:
                    response = await client.post(
                        '%s/authorizations' % api_url,
                        json=dict(username=user, password=user),
                        jwt=admin_jwt
                    )
                    token = test.json(response, 201)['id']
                    test_tokens[user] = token

                test_token = test_tokens[user]
                url = '%s%s' % (api_url, params.pop('api_url', '/%s' % name))
                method = params.pop('api_method', 'post')
                #
                # Allow to patch an existing model
                if method == 'patch' and name in app.models:
                    url = '%s/%s' % (
                        url, params.pop(app.models[name].id_field)
                    )
                response = await client.request(method, url, json=params,
                                                token=test_token)
                data = test.json(response)
                code = response.status_code
                if code > 201:
                    raise AssertionError('%s api call got %d: %s' %
                                         (url, code, data))
                total += 1

    logger.info('Created %s objects', total)


class TestMixin:
    app = None
    """Test class application"""
    config_file = 'tests.config'
    """The config file to use when building an :meth:`application`"""
    config_params = {}
    """Dictionary of parameters to override parameters from
    :attr:`config_file`
    """
    prefixdb = 'testlux_'

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
        self.assertEqual(response.headers['Content-Type'],
                         'text/html; charset=utf-8')
        return response.text

    def text(self, response, status_code=None):
        """Get JSON object from response
        """
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.headers['Content-Type'],
                         'text/plain; charset=utf-8')
        return response.text

    def json(self, response, status_code=None):
        """Get JSON object from response
        """
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.headers['Content-Type'],
                         'application/json; charset=utf-8')
        return response.json()

    def xml(self, response, status_code=None):
        """Get JSON object from response
        """
        from bs4 import BeautifulSoup
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertEqual(response.headers['Content-Type'],
                         'application/xml; charset=utf-8')
        return BeautifulSoup(response.text, 'xml')

    def empty(self, response, status_code=None):
        """Get JSON object from response
        """
        if status_code:
            self.assertEqual(response.status_code, status_code)
        self.assertFalse(response.content)

    def ws_upgrade(self, response):
        from lux.ext.sockjs import LuxWs
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

        self.assertTrue(data['error'])
        errors = dict(((d['field'], d['message'])
                       for d in data.get('errors', ())))
        errors[''] = data.get('message')
        msg = errors.get(field or '')
        if field is not None:
            self.assertTrue(msg)
        if text:
            self.assertEqual(msg, text)

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

    @classmethod
    def app_client(cls, app):
        return AppClient.create(app, False)


class AppTestCase(unittest.TestCase, TestMixin):
    """Test class for testing a single application
    """
    fixtures_path = None
    """path to fixtures"""
    odm = None
    """Original odm handler"""
    datastore = None
    """Test class datastore dictionary"""
    _test = TestCase()

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
        # admin JWT token for admin operations on Token auth backends
        cls.admin_jwt = await as_coroutine(cls.create_admin_jwt())
        await cls.populatedb()
        await cls.beforeAll()

    @classmethod
    async def tearDownClass(cls):
        if cls.odm:
            await cls.dropdb()
        await cls.afterAll()

    @classmethod
    def get_client(cls):
        return AppClient.create(cls.app, False)

    @classmethod
    def create_test_application(cls):
        """Return the lux application"""
        return test_app(cls)

    @classmethod
    def create_admin_jwt(cls):
        """Return the lux application"""
        return app_token(cls.app)

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
        cls.app.params['DATASTORE'] = cls.datastore
        cls.table_create()

    @classmethod
    def table_create(cls):
        cls.app.odm().table_create()

    @classmethod
    @green
    def dropdb(cls):
        cls.app.odm().close()
        cls.odm().database_drop(database=cls.dbname)

    @classmethod
    async def populatedb(cls):
        return load_fixtures(cls.app,
                             path=cls.fixtures_path,
                             api_url=cls.api_url(),
                             admin_jwt=cls.admin_jwt)

    @classmethod
    def api_url(cls, path=None):
        if 'API_URL' in cls.app.config:
            url = cls.app.config['API_URL']
            return remove_double_slash('%s/%s' % (url, path)) if path else url

    @classmethod
    def clone_app(cls):
        sapp = pickle.dumps(cls.app.callable)
        app = pickle.loads(sapp).setup(handler=False)
        if cls.datastore:
            app.config['DATASTORE'] = cls.datastore
        return TestApp(app)

    @classmethod
    async def beforeAll(cls):
        """Can be used to add logic before all tests"""

    @classmethod
    async def afterAll(cls):
        """Can be used to add logic after all tests"""

    @classmethod
    async def user_token(cls, credentials, **kw):
        '''Return a token for a user
        '''
        if isinstance(credentials, str):
            credentials = {"username": credentials,
                           "password": credentials}

        # Get new token
        response = await cls.client.post(cls.api_url('authorizations'),
                                         json=credentials, **kw)
        test = cls._test
        data = test.json(response, 201)
        test.assertTrue('id' in data)
        test.assertTrue('expiry' in data)
        test.assertTrue(data['session'])
        user = response.wsgi_request.cache.user
        test.assertTrue(user.is_anonymous())
        return data['id']

    def create_superuser(self, username, email, password):
        """A shortcut for the create_superuser command
        """
        return self.client.run_command('create_superuser',
                                       ['--username', username,
                                        '--email', email,
                                        '--password', password])


class WebApiTestCase(AppTestCase):
    """Test case for an api-web application pair
    """
    web_config_file = None
    web_config_params = None

    @classmethod
    async def setUpClass(cls):
        assert cls.web_config_file, "no web_config_file specified"
        await as_coroutine(super().setUpClass())
        params = cls.web_config_params or {}
        cls.web = test_app(cls, config_file=cls.web_config_file,
                           config_params=False, **params)
        for api in cls.web.apis:
            if api.netloc:
                cls.web.api.local_apps[api.netloc] = cls.app
        cls.webclient = AppClient.create(cls.web, False)

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
        url = self.web.config['REGISTER_URL']
        cookie, csrf = await self._cookie_csrf(url, csrf)
        username = randomname(prefix='u-')
        password = randomname()
        email = '%s@%s.com' % (username, randomname())
        data = {'username': username,
                'password': password,
                'password_repeat': password,
                'email': email}
        data.update(csrf)
        request = await self.webclient.post(url, json=data, cookie=cookie)
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


# INTERNALS

def _read_fixtures(fpath):
    for filename in os.listdir(fpath):
        if filename.endswith('.json'):
            with open(os.path.join(fpath, filename), 'r') as file:
                yield _json.load(file, object_pairs_hook=OrderedDict)
