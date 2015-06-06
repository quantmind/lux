import re
import os
from inspect import ismodule
from importlib import import_module
from itertools import chain

from sqlalchemy import Table
from sqlalchemy.ext.declarative import DeclarativeMeta

from pulsar import ImproperlyConfigured

import odm


Model = odm.Model


class Mapper(odm.Mapper):
    '''SQLAlchemy wrapper for lux applications
    '''

    def __init__(self, app, binds):
        self.app = app
        super().__init__(binds)
        self._autodiscover()

    def copy(self, binds):
        return self.__class__(self.app, binds)

    def session(self, **options):
        options['binds'] = self.binds
        return LuxSession(self, **options)

    def _autodiscover(self):
        # Setup models
        for label, mod in module_iterator(self.app.config['EXTENSIONS']):
            # Loop through attributes in mod_models
            for name in dir(mod):
                value = getattr(mod, name)
                if isinstance(value, (Table, DeclarativeMeta)):
                    self.register(value)


class LuxSession(odm.OdmSession):

    @property
    def app(self):
        return self.mapper.app


def module_iterator(application):
    '''Iterate over applications modules
    '''
    if ismodule(application) or isinstance(application, str):
        if ismodule(application):
            mod, application = application, application.__name__
        else:
            try:
                mod = import_module(application)
            except ImportError:
                # the module is not there
                mod = None
        if mod:
            label = application.split('.')[-1]
            try:
                mod_models = import_module('.models', application)
            except ImportError:
                mod_models = mod
            label = getattr(mod_models, 'APP_LABEL', label)
            yield label, mod_models
    else:
        for app in application:
            yield from module_iterator(app)
