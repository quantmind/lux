'''
Lux extension for integrating SQL and NoSQL into applications.

The extension create create a new application attribute called ``odm``
which can be used to access object data mappers for different backend.
To access the ``sql`` mapper:

    sql = app.odm('sql')

in a router handler:

    def get(self, request):
        sql = request.app.odm('sql')
        with sql.session().begin() as session:
            ...
'''
from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import WsgiHandler, wait_for_body_middleware
from pulsar.apps.greenio import WsgiGreen

import lux
from lux import Parameter
from lux.extensions.auth import RequirePermission

from .mapper import Odm
from .api import CRUD
from . import sql
from . import nosql


class Extension(lux.Extension):
    '''Object data mapper extension
    '''
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('GREEN_WSGI', 0,
                  'Run the WSGI handle in a pool of greenlet')]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        app.odm = Odm(app, app.config['DATASTORE'])

    def on_loaded(self, app):
        '''Wraps the Wsgi handler into a greenlet friendly handler
        '''
        if app.config['GREEN_WSGI']:
            green = WsgiGreen(app.handler)
            self.logger.info('Setup green Wsgi handler')
            app.handler = WsgiHandler((wait_for_body_middleware, green),
                                      async=True)
