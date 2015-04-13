import unittest
import string
import logging
import json
from unittest import mock
from io import StringIO

from pulsar import send
from pulsar.utils.httpurl import encode_multipart_formdata
from pulsar.utils.string import random_string
from pulsar.apps.test import test_timeout

import lux
from lux.core.commands.generate_secret_key import generate_secret

logger = logging.getLogger('lux.test')


def randomname(prefix=None):
    prefix = prefix or 'luxtest_'
    name = random_string(min_len=8, max_len=8, characters=string.ascii_letters)
    return ('%s%s' % (prefix, name)).lower()


def green(test_fun):

    def _(o):
        pool = o.app.green_pool
        if pool:
            return pool.submit(test_fun, o)
        else:
            return test_fun(o)

    return _


def test_app(test, config_file=None, argv=None, **params):
    '''Return an application for testing. Override if needed.
    '''
    kwargs = test.config_params.copy()
    kwargs.update(params)
    if 'EMAIL_BACKEND' not in kwargs:
        kwargs['EMAIL_BACKEND'] = 'lux.core.mail.LocalMemory'
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


class testClient:

    def __init__(self, app):
        self.app = app

    def run_command(self, command, argv=None, **kwargs):
        argv = argv or []
        cmd = self.app.get_command(command)
        return cmd(argv, **kwargs)

    def request_start_response(self, path=None, HTTP_ACCEPT=None,
                               headers=None, body=None, content_type=None,
                               **extra):
        extra['HTTP_ACCEPT'] = HTTP_ACCEPT or '*/*'
        if content_type:
            headers = headers or []
            headers.append(('content-type', content_type))
        request = self.app.wsgi_request(path=path, headers=headers, body=body,
                                        extra=extra)
        start_response = mock.MagicMock()
        return request, start_response

    def request(self, **params):
        request, sr = self.request_start_response(**params)
        response = self.app(request.environ, sr)
        return request

    def get(self, path=None, **extra):
        extra['REQUEST_METHOD'] = 'GET'
        return self.request(path=path, **extra)

    def post(self, path=None, body=None, content_type=None, **extra):
        extra['REQUEST_METHOD'] = 'POST'
        if body and not isinstance(body, bytes):
            if content_type is None:
                body, content_type = encode_multipart_formdata(body)
            elif content_type == 'application/json':
                body = json.dumps(body).encode('utf-8')

        return self.request(path=path, content_type=content_type,
                            body=body, **extra)


class TestMixin:
    config_file = 'tests.config'
    '''The config file to use when building an :meth:`application`'''
    config_params = {}
    '''Dictionary of parameters to override the parameters from
    :attr:`config_file`'''
    prefixdb = 'luxtest_'

    def bs(self, response):
        from bs4 import BeautifulSoup
        self.assertEqual(response.headers['content-type'],
                         'text/html; charset=utf-8')
        return BeautifulSoup(response.get_content())

    def authenticity_token(self, doc):
        name = doc.find('meta', attrs={'name': 'csrf-param'})
        value = doc.find('meta', attrs={'name': 'csrf-token'})
        if name and value:
            name = name.attrs['content']
            value = value.attrs['content']
            return {name: value}


class TestCase(unittest.TestCase, TestMixin):
    '''TestCase class for lux tests.

    It provides several utilities methods.
    '''
    apps = None

    def application(self, config_file=None, argv=None, **params):
        '''Return an application for testing. Override if needed.
        '''
        kwargs = self.config_params.copy()
        kwargs.update(params)
        if 'EMAIL_BACKEND' not in kwargs:
            kwargs['EMAIL_BACKEND'] = 'lux.core.mail.LocalMemory'
        config_file = config_file or self.config_file
        if argv is None:
            argv = []
        if '--log-level' not in argv:
            argv.append('--log-level')
            levels = self.cfg.loglevel if hasattr(self, 'cfg') else ['none']
            argv.extend(levels)
        app = lux.App(config_file, argv=argv, **kwargs).setup()
        self.on_loaded(app)
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

    def request(self, app=None, **params):
        if not app:
            app = self.application()
        request, sr = self.request_start_response(app, **params)
        response = app(request.environ, sr)
        self.assertEqual(response, request.response)
        return request

    def run_command(self, app, *args, **kwargs):
        if not args:
            command = app
            app = self.application()
        else:
            command = args[0]
        argv = args[1] if len(args) == 2 else []
        cmd = app.get_command(command)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd(argv, **kwargs)

    def fetch_command(self, command, out=None):
        '''Fetch a command.'''
        app = self.application()
        cmd = app.get_command(command)
        self.assertTrue(cmd.logger)
        self.assertEqual(cmd.name, command)
        return cmd

    def post(self, app=None, path=None, content_type=None, body=None,
             headers=None, **extra):
        extra['REQUEST_METHOD'] = 'POST'
        headers = headers or []
        if body and not isinstance(body, bytes):
            if content_type is None:
                body, content_type = encode_multipart_formdata(body)
        if content_type:
            headers.append(('content-type', content_type))
        return self.request(app, path=path, headers=headers,
                            body=body, **extra)

    def database_drop(self):
        if self.apps:
            for app in self.apps:
                if hasattr(app, 'mapper'):
                    from lux.extensions.odm import database_drop
                    yield from database_drop(app)

    def tearDown(self):
        return self.database_drop()


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
        cls.client = testClient(cls.app)
        if hasattr(cls.app, 'odm'):
            cls.odm = cls.app.odm
            return cls.setupdb()

    @classmethod
    @green
    def tearDownClass(cls):
        if cls.odm:
            cls.app.odm().close()
            cls.odm().database_drop(database=cls.dbname)

    @classmethod
    def dbname(cls, engine):
        if engine not in cls.dbs:
            cls.dbs[engine] = randomname(cls.prefixdb)
        return cls.dbs[engine]

    @classmethod
    @green
    def setupdb(cls):
        logger.info('Create test databases')
        cls.app.odm = cls.odm.database_create(database=cls.dbname)
        logger.info('Create test tables')
        cls.app.odm().table_create()


class TestServer(unittest.TestCase, TestMixin):
    app_cfg = None

    @test_timeout(30)
    @classmethod
    def setUpClass(cls):
        name = cls.__name__.lower()
        cfg = cls.cfg
        argv = [__file__, 'serve', '-b', '127.0.0.1:0',
                '--concurrency', cfg.concurrency]
        loglevel = cfg.loglevel
        cls.app = app = lux.execute_from_config(cls.config_file, argv=argv,
                                                name=name, loglevel=loglevel)
        mapper = cls.on_loaded(app)
        if mapper:
            app.params['DATASTORE'] = mapper._default_store.dns
            yield from app.get_command('create_databases')([])
            yield from app.get_command('create_tables')([])
        cls.app_cfg = yield from app._started
        cls.url = 'http://{0}:{1}'.format(*cls.app_cfg.addresses[0])

    @classmethod
    def tearDownClass(cls):
        from lux.extensions.odm import database_drop
        if cls.app_cfg is not None:
            yield from send('arbiter', 'kill_actor', cls.app_cfg.name)
            yield from database_drop(cls.app)
