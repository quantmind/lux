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
import lux
from lux import Parameter

from .mapper import Odm
from .api import CRUD
from . import sql
from . import nosql


class Extension(lux.Extension):
    '''Object data mapper extension
    '''
    _config = [
        Parameter('DATASTORE', None,
                  'Dictionary for mapping models to their back-ends database')
    ]

    def on_config(self, app):
        '''Initialise Object Data Mapper'''
        app.odm = Odm(app, app.config['DATASTORE'])
