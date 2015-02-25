from pulsar import ImproperlyConfigured
from pulsar.apps.greenio import WsgiGreen
from pulsar.utils.log import LocalMixin

import lux
from lux import Parameter

import odm
from odm.green import GreenMapper


class Extension(lux.Extension):
    '''Object data mapper extension
    '''
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('SEARCHENGINE', None,
                  'Search engine for models')]

    def on_loaded(self, app):
        '''Build the API middleware.

        If :setting:`API_URL` is defined, it loops through all extensions
        and checks if the ``api_sections`` method is available.
        '''
        app.mapper = AppMapper(app)
        app.handler = WsgiGreen(app.handler)


class AppMapper(LocalMixin):

    def __init__(self, app):
        self.app = app

    def __call__(self):
        if not self.local.mapper:
            self.local.mapper = self.create_mapper()
        return self.local.mapper

    def create_mapper(self):
        datastore = self.app.config['DATASTORE']
        if not datastore:
            return
        elif isinstance(datastore, str):
            datastore = {'default': datastore}
        if 'default' not in datastore:
            raise ImproperlyConfigured('default datastore not specified')
        mapper = GreenMapper(datastore['default'])
        mapper.register_applications(self.app.config['EXTENSIONS'])
        return mapper

