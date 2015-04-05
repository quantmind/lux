import asyncio

from pulsar import InvalidOperation, ImproperlyConfigured, EventHandler
from pulsar.apps.data import NoSuchStore
from pulsar.apps.greenio import wait

from .transaction import Transaction, ModelDictionary
from .store import create_store, ascoro
from .manager import Manager
from .models import ModelType
from ..mapper import Mapper


class NoSQL(Mapper):
    '''NoSQL mapper.'''

    _engines = None

    def database_create(self, **params):
        '''Create databases and return a new :class:`.Odm`
        '''
        binds = {}
        for engine in self.engines():
            binds.update(engine.database_create(**params))
        return binds

    def database_drop(self, **params):
        for engine in self.engines():
            wait(engine.database_drop(**params))

    def register(self, module, *args, **params):
        '''Register Models from ``module``
        '''
        self._setup()
        include_related = params.pop('include_related', True)
        # Loop through attributes in mod_models
        for name in dir(module):
            value = getattr(module, name)
            for model in models_from_model(value,
                                           include_related=include_related):
                if model in self.binds:
                    continue
                if not isinstance(model, ModelType):
                    continue
                label = model._meta.app_label
                if label:
                    engine = self._engines.get(label)
                if not engine:
                    engine = self._engines.get(None)
                if engine:
                    self.binds[model] = engine

    def session(self, **options):
        return Transaction(self, **options)
    begin = session

    def engines(self):
        self._setup()
        return self._engines.values()

    def close(self):
        for engine in self.engines():
            wait(engine.close())

    def table_create(self, remove_existing=False):
        '''Loop though :attr:`registered_models` and issue the
        :meth:`.Manager.create_table` method.'''
        for manager in self:
            yield from manager.table_create(remove_existing)

    def table_drop(self):
        '''Loop though :attr:`registered_models` and issue the
        :meth:`.Manager.drop_table` method.'''
        for manager in self:
            yield from manager.table_drop()

    def tables(self):
        raise NotImplementedError

    # PRIVATE METHODS
    def _setup(self):
        if self._engines is not None:
            return
        binds = self.binds
        self._engines = {}
        self.binds = ModelDictionary()
        # Create all sql engines in the binds dictionary
        # Quietly fails if the engine is not recognised,
        # it my be a NoSQL store
        for name, bind in tuple(binds.items()):
            key = None if name == 'default' else name
            try:
                self._engines[key] = create_store(binds[name])
            except NoSuchStore:
                pass
            else:
                binds.pop(name)


def valid_model(model):
    if isinstance(model, ModelType):
        return not model._meta.abstract
    return False


def models_from_model(model, include_related=False, exclude=None):
    '''Generator of all model in model.

    :param model: a :class:`.Model`
    :param include_related: if ``True`` al related models to ``model``
        are included
    :param exclude: optional set of models to exclude
    '''
    if exclude is None:
        exclude = set()
    if valid_model(model) and model not in exclude:
        exclude.add(model)
        yield model
        if include_related:
            for column in model._meta.dfields.values():
                for fk in column.foreign_keys:
                    for model in (fk.column.table,):
                        for m in models_from_model(
                                model, include_related=include_related,
                                exclude=exclude):
                            yield m
