import lux

from lux import forms, HtmlRouter
from lux.extensions import odm

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']

AUTHENTICATION_BACKENDS = ['lux.extensions.auth.SessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend',
                           'lux.extensions.auth.BrowserBackend']

API_URL = 'api'
SESSION_COOKIE_NAME = 'test-sessions'
CACHE_SERVER = 'redis://127.0.0.1:6'


class Extension(lux.Extension):

    def middleware(self, app):
        return [HtmlRouter('/')]
