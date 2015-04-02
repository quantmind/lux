from inspect import ismethod

from pulsar.apps.greenio import wait

from .mapper import Mapper
from .manager import QueryMixin


class GreenMapper(Mapper):
    '''A :class:`~odm.Mapper` which runs asynchronous method on a
    greenlet pool
    '''
    def _register(self, manager):
        super()._register(GreenManager(manager))

    def table_create(self, remove_existing=False):
        return wait(super().table_create(remove_existing))

    def table_drop(self):
        return wait(super().table_drop())

    def commit(self, transaction):
        return wait(super().commit(transaction))


class GreenObject:

    def __init__(self, manager):
        self.manager = manager

    def __getattr__(self, name):
        attr = getattr(self.manager, name)
        return greentask(attr) if ismethod(attr) else attr

    def __repr__(self):
        return self.manager.__repr__()

    def __str__(self):
        return self.manager.__str__()


class GreenManager(GreenObject, QueryMixin):

    def compile_query(self, query):
        return GreenObject(super().compile_query(query))


class greentask:
    __slots__ = ('_callable',)

    def __init__(self, callable):
        self._callable = callable

    def __call__(self, *args, **kw):
        return wait(self._callable(*args, **kw))

    def __repr__(self):
        return self._callable.__repr__()
