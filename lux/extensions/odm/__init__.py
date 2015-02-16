from pulsar import ImproperlyConfigured
from pulsar.apps.greenio import GreenPool

import lux
from lux import Parameter

import odm
from odm.green import GreenMapper


class Extension(lux.Extension):

    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('SEARCHENGINE', None,
                  'Search engine for models'),
        Parameter('USEGREENLET', True,
                  ('Use the greenlet package for implicit asynchronous '
                   'paradigm'))]

    def on_loaded(self, app):
        '''Build the API middleware.

        If :setting:`API_URL` is defined, it loops through all extensions
        and checks if the ``api_sections`` method is available.
        '''
        datastore = app.config['DATASTORE']
        if not datastore:
            return
        if 'default' not in datastore:
            raise ImproperlyConfigured('default datastore not specified')
        if app.config['USEGREENLET']:
            app.mapper = GreenMapper(datastore['default'])
        else:
            app.mapper = odm.Mapper(datastore['default'])
        app.mapper.register_applications(app.config['EXTENSIONS'])
        if app.config['USEGREENLET']:
            app.handler = run_in_green_pool(app.handler)


class run_in_green_pool:

    def __init__(self, middleware, max_workers=None):
        self.middleware = middleware
        self.max_workers = max_workers
        self.pool = None

    def __call__(self, environ, start_response):
        if self.pool is None:
            self.pool = GreenPool(max_workers=self.max_workers)

        return self.pool.submit(self.middleware, environ, start_response)
