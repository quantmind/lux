import lux
from lux import Router, Html

from tests.config import *

SECRET_KEY = 'PHCWf8hiGtk65l19FnoVnypaWe2AYGY3XerbM2GDs45Oq5Az4O'
SESSION_COOKIE_NAME = 'luxtest'

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.api',
              'lux.extensions.ui',
              'lux.extensions.angular',
              'lux.extensions.code',
              'lux.extensions.cms',
              'lux.extensions.odm']

AUTHENTICATION_BACKEND = 'lux.extensions.auth.models.SessionBackend'


class Extension(lux.Extension):

    def middleware(self, app):
        return [Router('/', get=self.home)]

    def home(self, request):
        doc = request.html_document
        doc.body.append(Html('div',
                             '<p>Well done, Site is created!</p>'))
        return doc.http_response(request)
