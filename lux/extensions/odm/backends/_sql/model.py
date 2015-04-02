from functools import wraps

import sqlalchemy as sql
from sqlalchemy import orm, Column
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from pulsar import Http404

from ...query import QueryMixin
from ...manager import Manager
from ...models import meta_mixin, Meta


metadata = sql.MetaData()
sql._Table = sql.Table


def _make_table():
    def _make_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], sql.Column):
            args = (args[0], metadata) + args[1:]
        info = kwargs.pop('info', None) or {}
        info.setdefault('bind_key', None)
        kwargs['info'] = info
        return sql._Table(*args, **kwargs)

    return _make_table


def in_executor(method):

    @wraps(method)
    def _(self, *args, **kwargs):
        return self._loop.run_in_executor(None, method, self, *args, **kwargs)

    return _


class BaseQuery(orm.Query, QueryMixin):
    """The default query object used for models, and exposed as
    :attr:`~SQLAlchemy.Query`. This can be subclassed and
    replaced for individual models by setting the :attr:`~Model.query_class`
    attribute.  This is a subclass of a standard SQLAlchemy
    :class:`~sqlalchemy.orm.query.Query` class and has all the methods of a
    standard query as well.
    """
    pass


class SqlManager(Manager):

    @property
    def _meta(self):
        return self._model._meta

    def query(self):
        '''Build a :class:`.Query` object
        '''
        return self._store.session().query(self._model)

    def table_create(self, remove_existing=False):
        '''Create the table/collection for the :attr:`_model`
        '''
        yield from self._store.table_create(self._model, remove_existing)
        if self._mapper.search_engine:
            yield from self._mapper.search_engine.create_table(self)

    def table_drop(self, remove_existing=False):
        '''Create the table/collection for the :attr:`_model`
        '''
        yield from self._store.table_create(self._model, remove_existing)
        if self._mapper.search_engine:
            yield from self._mapper.search_engine.create_table(self)


class SqlModelType(DeclarativeMeta):

    def __new__(cls, name, bases, attrs):
        meta = Meta(name, **meta_mixin(attrs))
        if '__table__' in attrs:
            meta.table_name = attrs['__table__'].name
        elif cls._is_abstract(meta, bases, attrs):
            meta.abstract = True
            attrs['__abstract__'] = True
        else:
            attrs['__tablename__'] = meta.table_name
        new_class = DeclarativeMeta.__new__(cls, name, bases, attrs)
        new_class._meta = meta
        meta.model = new_class
        return new_class

    def __init__(self, name, bases, d):
        bind_key = d.pop('__bind_key__', None)
        DeclarativeMeta.__init__(self, name, bases, d)
        if bind_key is not None:
            self.__table__.info['bind_key'] = bind_key

    @classmethod
    def _is_abstract(cls, meta, bases, d):
        if meta.abstract:
            return True

        if any(v.primary_key for v in d.values() if isinstance(v, Column)):
            return False

        for base in bases:
            if hasattr(base, '__tablename__'):
                meta.table_name = base.__tablename__
                return False
            elif hasattr(base, '__table__'):
                meta.table_name = base.__table__.name
                return False

            for name in dir(base):
                attr = getattr(base, name)

                if isinstance(attr, sql.Column) and attr.primary_key:
                    return False

        return True


class ModelBase:
    """Baseclass for custom user models."""

    #: the query class used.  The :attr:`query` attribute is an instance
    #: of this class.  By default a :class:`BaseQuery` is used.
    query_class = BaseQuery

    #: an instance of :attr:`query_class`.  Can be used to query the
    #: database for instances of this model.
    query = None


sql.Model = declarative_base(cls=ModelBase,
                             name='Model',
                             metadata=metadata,
                             metaclass=SqlModelType)


sql.Table = _make_table()
