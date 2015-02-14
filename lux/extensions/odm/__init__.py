from pulsar import ImproperlyConfigured

import lux
from lux import Parameter

import odm


class Extension(lux.Extension):

    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database'),
        Parameter('SEARCHENGINE', None,
                  'Search engine for models')]

    def on_config(self, app):
        '''Build the API middleware.

        If :setting:`API_URL` is defined, it loops through all extensions
        and checks if the ``api_sections`` method is available.
        '''
        datastore = app.config['DATASTORE']
        if not datastore:
            return
        if 'default' not in datastore:
            raise ImproperlyConfigured('default datastore not specified')
        mapper = odm.Mapper(datastore['default'])
        mapper.register_applications(app.config['EXTENSIONS'])
