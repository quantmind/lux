from lux.core import HtmlRouter, LuxExtension

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']

AUTHENTICATION_BACKENDS = ['lux.extensions.auth.SessionBackend',
                           'lux.extensions.rest.backends.CsrfBackend',
                           'lux.extensions.auth.BrowserBackend']

SESSION_COOKIE_NAME = 'test-sessions'
CACHE_SERVER = 'redis://127.0.0.1:6'


class Extension(LuxExtension):

    def middleware(self, app):
        return [HtmlRouter('/')]
