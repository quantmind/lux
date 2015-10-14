import lux
from lux.extensions.cms import AnyPage

from tests.config import *  # noqa


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth',
              'lux.extensions.cms']

API_URL = 'api'


class Extension(lux.Extension):

    def meddleware(self, app):
        return [AnyPage('wiki')]

    def on_loaded(self, app):
        '''Add the AnyPage router for serving pages
        '''
        app.handler.middleware.append(AnyPage())
