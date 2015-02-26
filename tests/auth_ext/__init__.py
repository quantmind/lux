import lux
from lux import Router

from tests.config import *

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.api',
              'lux.extensions.auth',
              'lux.extensions.odm']

AUTHENTICATION_BACKEND = 'lux.extensions.auth.models.SessionBackend'


class Extension(lux.Extension):

    def middleware(self, app):
        return [Router('/', get=self.home)]

    def home(self, request):
        doc = request.html_document
        doc.body.append(Html('div',
                             '<p>Well done, TARS is created!</p>'))
        return doc.http_response(request)
