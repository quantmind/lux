import re
from copy import copy

from abc import ABCMeta, abstractmethod
from inspect import ismodule
from importlib import import_module
from collections import OrderedDict

from pulsar import ImproperlyConfigured
from pulsar.utils.log import LocalMixin


_mappers = OrderedDict()
_camelcase_re = re.compile(r'([A-Z]+)(?=[a-z0-9])')


class MapperType(ABCMeta):
    '''Metaclass for Object data mappers
    '''
    def __new__(cls, name, bases, attrs):
        key = attrs.pop('name', name).lower()
        abstract = attrs.pop('__abstract__', False)
        mapper_class = super().__new__(cls, name, bases, attrs)
        if not abstract:
            _mappers[key] = mapper_class
        return mapper_class


class Mapper(metaclass=MapperType):
    '''Base class for lux object data mappers
    '''
    __abstract__ = True

    def __init__(self, app, binds):
        self.app = app
        self.binds = binds

    def __repr__(self):
        return '%s %s' % (self.__class__.__name__, self)

    def __str__(self):
        return str(self.binds)

    @abstractmethod
    def register(self, module, label, **params):
        '''Register models defined in ``module`` with this mapper
        '''
        pass

    @abstractmethod
    def database_create(self, **params):
        '''Create databases and return a new mapper
        '''
        pass

    @abstractmethod
    def database_drop(self, **params):
        '''Drop all databases associated with this mapper
        '''
        pass

    @abstractmethod
    def table_create(self, remove_existing=False):
        '''Create all tables associated with this mapper
        '''
        pass

    @abstractmethod
    def table_drop(self, bind='__all__'):
        '''Drop all tables associated with this mapper
        '''
        pass

    @abstractmethod
    def tables(self):
        '''List all tables for this mapper
        '''
        pass

    @abstractmethod
    def session(self, **params):
        '''Obtain a session for this mapper
        '''
        pass

    @abstractmethod
    def engines(self):
        '''List of datastore engines
        '''
        pass

    @abstractmethod
    def begin(self, **params):
        '''Close the backend connections
        '''
        pass

    @abstractmethod
    def close(self):
        '''Close the backend connections
        '''
        pass


class Odm(Mapper, LocalMixin):
    '''Lazy object data mapper container

    Usage:

        sql = app.odm('sql')
    '''
    __abstract__ = True

    def __call__(self, key):
        return self.mappers()[key]

    def __iter__(self):
        return iter(self.mappers().values())

    def __len__(self):
        return len(self.mappers())

    def mappers(self):
        if self.local.mappers is None:
            self.local.mappers = self._autodiscover()
        return self.local.mappers

    def database_create(self, **params):
        '''Create databases and return a new :class:`.Odm`
        '''
        binds = {}
        for mapper in self:
            binds.update(mapper.database_create(**params))
        return self.__class__(self.app, binds)

    def database_drop(self, **params):
        for mapper in self:
            mapper.database_drop(**params)

    def table_create(self, remove_existing=False):
        for mapper in self.mappers().values():
            mapper.table_create(remove_existing)

    def table_drop(self):
        for mapper in self.mappers().values():
            mapper.table_drop()

    def tables(self):
        '''Return a list of tables associated with this mapper
        '''
        tables = []
        for mapper in self.mappers().values():
            tables.extend(mapper.tables())
        return tables

    def engines(self):
        engines = []
        for mapper in self:
            engines.extend(mapper.engines())
        return engines

    def close(self):
        for mapper in self:
            mapper.close()

    def register(self, module, label, **params):
        pass

    def begin(self, **params):
        raise NotImplementedError

    def session(self, **params):
        raise NotImplementedError

    def _autodiscover(self):
        datastore = self.binds
        if not datastore:
            datastore = {}
        elif isinstance(datastore, str):
            datastore = {'default': datastore}
        if datastore and 'default' not in datastore:
            raise ImproperlyConfigured('default datastore not specified')

        self.binds = datastore
        return register_applications(self.app,
                                     copy(datastore),
                                     self.app.config['EXTENSIONS'],
                                     green=self.app.config['GREEN_WSGI'])


def model_label(attrs):
    label = attrs.pop('__label__', None)
    if not label and '__module__' in attrs:
        bits = attrs['__module__'].split('.')
        label = bits.pop()
        if label == 'models':
            label = bits.pop()
    return label


def model_name(name):
    return _camelcase_re.sub(_join, name).lstrip('_')


def register_applications(app, binds, applications, **params):
    '''A higher level registration method for group of models located
    on application modules.

    It uses the :meth:`model_iterator` method to iterate
    through all :class:`.Model` available in ``applications``
    and :meth:`register` them.

    :parameter applications: A String or a list of strings representing
        python dotted paths where models are implemented. Can also be
        a module or a list of modules.
    :parameter models: Optional list of models to include. If not provided
        all models found in *applications* will be included.
    :parameter binds: dictionary which map a model or an
        application to a store
        :ref:`connection string <connection-string>`.
    :rtype: A list of registered :class:`.Model`.

    For example::


        register_applications('mylib.myapp')
        register_applications(['mylib.myapp', 'another.path'])
        register_applications(pythonmodule)
        register_applications(['mylib.myapp', pythonmodule])

    '''
    mappers = {}
    for key, MapperClass in _mappers.items():
        mapper = MapperClass(app, binds)
        for label, mod in module_iterator(applications):
            mapper.register(mod, label, **params)
        mappers[key] = mapper
    return mappers


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


def _join(match):
    word = match.group()
    if len(word) > 1:
        return ('_%s_%s' % (word[:-1], word[-1])).lower()
    return '_' + word.lower()
