import unittest
import string
from unittest import mock
from io import StringIO

from pulsar.utils.httpurl import encode_multipart_formdata
from pulsar.utils.string import random_string
from pulsar.apps.http import HttpClient

import lux


def randomname():
    return random_string(min_len=8, max_len=8,
                         characters=string.ascii_letters)


class TestCase(unittest.TestCase):
    '''TestCase class for lux tests.

    It provides several utilities methods.
    '''
    config_file = 'tests.config'
    '''THe config file to use when building an :meth:`application`'''
    config_params = {}
    '''Dictionary of parameters to override the parameters from
    :attr:`config_file`'''
    apps = None

    @classmethod
    def on_loaded(cls, app):
        app.stdout = StringIO()
        app.stderr = StringIO()
        if hasattr(app, 'mapper'):
            mapper = app.mapper()
            dbname = randomname()
            mapper.default_store.database = dbname
            for manager in mapper:
                manager._store.database = dbname
        return app

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

    def authenticity_token(self, doc):
        name = doc.find('meta', attrs={'name': 'csrf-param'})
        value = doc.find('meta', attrs={'name': 'csrf-token'})
        if name and value:
            name = name.attrs['content']
            value = value.attrs['content']
            return {name: value}

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


class TestServer(unittest.TestCase):
    config_file = 'tests.config'
    app_cfg = None

    @classmethod
    def setUpClass(cls):
        name = cls.__name__.lower()
        cfg = cls.cfg
        argv = [__file__, 'serve', '-b', '127.0.0.1:0',
                '--concurrency', cfg.concurrency]
        cls.app = app = lux.execute_from_config(cls.config_file, argv=argv,
                                                name=name)
        cls.on_loaded(app)
        cls.app_cfg = yield from app._started
        yield from app.get_command('create_databases')([])
        yield from app.get_command('create_tables')([])
        yield from app.get_command('create_superuser')([], interactive=False,
                                                       username='pippo',
                                                       password='pluto')
        cls.url = 'http://{0}:{1}'.format(*cls.app_cfg.addresses[0])
        cls.http = HttpClient()
        # Create databases

    @classmethod
    def tearDownClass(cls):
        from lux.extensions.odm import database_drop
        if cls.app_cfg is not None:
            yield from send('arbiter', 'kill_actor', cls.app_cfg.name)
            yield from database_drop(cls.app)
