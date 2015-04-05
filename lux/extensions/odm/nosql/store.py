from pulsar import is_async
from pulsar.apps import data

from lux import forms

create_store = data.create_store
register_store = data.register_store
Command = data.Command
REV_KEY = '_rev'


class OdmMixin:
    ModelType = None
    '''Model type for a store
    '''
    _loop = None

    def create_model(self, manager, *args, **kwargs):
        '''Create a new model from a ``manager``
        Method used by the :class:`.Manager` callable method.
        '''
        instance = manager._model(*args, **kwargs)
        instance['_mapper'] = manager._mapper
        return instance

    def transaction(self):
        '''Create a transaction for this store.
        '''
        return StoreTransaction(self)

    def execute_transaction(self, transaction):
        '''Execute a  :meth:`transaction` in a multi-store
        :class:`.Transaction`.

        THis methid is used by the :ref:`object data mapper <odm>` and
        should not be invoked directly.
        It returns a list of models committed to the backend server.
        '''
        raise NotImplementedError

    def compile_query(self, query):
        '''Compile the :class:`.Query` ``query``.

        Method required by the :class:`Object data mapper <odm>`.

        :return: an instance of :class:`.CompiledQuery` if implemented
        '''
        raise NotImplementedError

    def get_model(self, manager, pkvalue):
        '''Fetch an instance of a ``model`` with primary key ``pkvalue``.

        This method required by the :ref:`object data mapper <odm>`.

        :param manager: the :class:`.Manager` calling this method
        :param pkvalue: the primary key of the model to retrieve
        '''
        raise NotImplementedError

    def has_query(self, query_type):
        '''Check if this :class:`.Store` supports ``query_type``.

        :param query_type: a string indicating the query type to check
            (``filter``, ``exclude``, ``search``).

        This method is used by the :ref:`object data mapper <odm>`.
        '''
        return True

    def model_data(self, model, action=None):
        if not action:
            action = Command.UPDATE if REV_KEY in model else Command.INSERT
        return (dict(model._meta.store_data(model, self, action)), action)

    def datetime(self, value):
        return value


class StoreTransaction(object):
    '''Transaction for a given :class:`.Store`
    '''
    def __init__(self, store):
        self.store = store
        self.commands = []

    def add(self, model, action=None):
        self.commands.append(Command(model, action))
        return model


class Store(data.Store, OdmMixin):
    pass


class RemoteStore(data.RemoteStore, OdmMixin):
    ModelNotFound = forms.ModelNotFound


class DummyStore(Store):
    pass


def ascoro(result=None):
    if is_async(result):
        result = yield from result
    return result


register_store("dummy", "lux.extensions.odm.nosql.DummyStore")
