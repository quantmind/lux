import json
from datetime import date, datetime
from enum import Enum
from functools import partial

import pytz

from sqlalchemy import Column, desc, String
from sqlalchemy.orm import class_mapper, load_only
from sqlalchemy.orm.base import instance_state
from sqlalchemy.sql.expression import func, cast
from sqlalchemy.exc import DataError, StatementError
from sqlalchemy.orm.exc import (NoResultFound, MultipleResultsFound,
                                ObjectDeletedError)

from pulsar import Http404

from odm.utils import get_columns

from lux.core import app_attribute, ModelNotAvailable, Query as BaseQuery
from lux.utils.crypt import as_hex
from lux.extensions import rest

MissingObjectError = (DataError, NoResultFound, StatementError)

RestField = rest.RestField
is_rel_field = rest.is_rel_field


class Query(BaseQuery):
    """ODM based query"""

    def __init__(self, model, session):
        super().__init__(model, session)
        self.request = session.request
        self.sql_query = session.query(model.db_model())
        self.joins = set()
        self.app.fire('on_query', self)

    @property
    def logger(self):
        return self.request.logger

    def count(self):
        return self._query().count()

    def one(self):
        query = self._query()
        try:
            one = query.one()
        except MissingObjectError:
            raise Http404
        except MultipleResultsFound:
            self.logger.error('%s - Multiple result found for model %s. '
                              'Returning the first' %
                              (self.request.first_line, self.name))
            one = query.first()
        return self.model.instance(one, self.fields)

    def all(self):
        model = self.model
        fields = self.fields
        return [model.instance(o, fields) for o in self._query().all()]

    def delete(self):
        return self._query().delete()

    def limit(self, limit):
        self.sql_query = self.sql_query.limit(limit)
        return self

    def offset(self, offset):
        self.sql_query = self.sql_query.offset(offset)
        return self

    def filter_args(self, *filters):
        if filters:
            self.sql_query = self.sql_query.filter(*filters)
        return self

    def filter_field(self, field, op, value):
        """
        Applies a filter on a field.

        Notes on 'ne' op:

        Example data: [None, 'john', 'roger']
        ne:john would return only roger (i.e. nulls excluded)
        ne:     would return john and roger


        Notes on  'search' op:

        For some reason, SQLAlchemy uses to_tsquery rather than
        plainto_tsquery for the match operator

        to_tsquery uses operators (&, |, ! etc.) while
        plainto_tsquery tokenises the input string and uses AND between
        tokens, hence plainto_tsquery is what we want here

        For other database back ends, the behaviour of the match
        operator is completely different - see:
        http://docs.sqlalchemy.org/en/rel_1_0/core/sqlelement.html

        :param field:       field name
        :param op:          'eq', 'ne', 'gt', 'lt', 'ge', 'le' or 'search'
        :param value:       comparison value, string or list/tuple
        :return:
        """
        app = self.app
        odm = app.odm()
        query = self.sql_query

        if field.model:
            field_model = self.app.models.get(field.model)
            if not field_model:
                return
            db_model = field_model.db_model()
            field = getattr(db_model, field.name, None)
            if field is None:
                field = getattr(db_model, field_model.id_field, None)
            if not field:
                return
            if field_model.identifier not in self.joins:
                self.joins.add(field_model.identifier)
                query = query.join(db_model)
        elif isinstance(field.field, str):
            field = getattr(self.model.db_model(), field.name, None)
        else:
            field = None

        if not field:
            return

        multiple = isinstance(value, (list, tuple))

        if value == '':
            value = None

        if multiple and op in ('eq', 'ne'):
            if op == 'eq':
                query = query.filter(field.in_(value))
            elif op == 'ne':
                query = query.filter(~field.in_(value))
        else:
            if multiple:
                assert len(value) > 0
                value = value[0]

            if op == 'eq':
                query = query.filter(field == value)
            elif op == 'ne':
                query = query.filter(field != value)
            elif op == 'search':
                dialect_name = odm.binds[odm[self.name].__table__].dialect.name
                if dialect_name == 'postgresql':
                    ts_config = field.info.get(
                        'text_search_config',
                        app.config['DEFAULT_TEXT_SEARCH_CONFIG']
                    )
                    query = query.filter(
                        func.to_tsvector(ts_config, cast(field, String)).op(
                            '@@')(func.plainto_tsquery(value))
                    )
                else:
                    query = query.filter(field.match(value))
            elif op == 'gt':
                query = query.filter(field > value)
            elif op == 'ge':
                query = query.filter(field >= value)
            elif op == 'lt':
                query = query.filter(field < value)
            elif op == 'le':
                query = query.filter(field <= value)
        self.sql_query = query
        return self

    def sortby_field(self, entry, direction):
        fields = self.model.db_columns()
        if entry in fields:
            if direction == 'desc':
                entry = desc(entry)
            self.sql_query = self.sql_query.order_by(entry)
        return self

    def _query(self):
        if self.fields:
            fields = self.model.db_columns(self.fields)
            self.sql_query = self.sql_query.options(load_only(*fields))
        return self.sql_query


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    def register(self, app):
        super().register(app)
        odm_models(app)[self.name] = self

    # LuxModel VIRTUAL METHODS
    def session(self, request, session=None):
        return self.app.odm().begin(request=request, session=session)

    def get_query(self, session):
        return Query(self, session)

    def create_instance(self):
        """Return an instance of the Sql model"""
        return self.db_model()()

    def tojson(self, request, instance, in_list=False, exclude=None,
               exclude_related=None, safe=False, **kw):
        instance = self.instance(instance)
        obj = instance.obj
        if instance_state(obj).detached:
            with self.session(request) as session:
                session.add(obj)
                return self.tojson(request, instance, in_list=in_list,
                                   exclude_related=exclude_related, safe=safe,
                                   exclude=exclude, **kw)
        info = self._fields
        exclude = info.exclude(exclude, exclude_urls=True)
        load_only = instance.fields

        fields = {}
        for field in self.fields().values():
            name = field.name
            if name in exclude or (load_only and name not in load_only):
                continue
            try:
                data = self.get_instance_value(instance, name)
                if isinstance(data, date):
                    if isinstance(data, datetime) and not data.tzinfo:
                        data = pytz.utc.localize(data)
                    data = data.isoformat()
                elif isinstance(data, Enum):
                    data = data.name
                elif is_rel_field(field):
                    if exclude_related:
                        continue
                    model = request.app.models.get(field.model)
                    if model:
                        data = self._related_model(request, model, data,
                                                   in_list)
                    else:
                        data = None
                        request.logger.error(
                            'Could not find model %s', field.model)
                else:  # Test Json
                    json.dumps(data)
            except TypeError:
                try:
                    data = str(data)
                except Exception:
                    continue
            except ObjectDeletedError:
                raise ModelNotAvailable from None
            except Exception:
                if not safe:
                    request.logger.exception(
                        'Exception while converting attribute "%s" in model '
                        '%s to JSON', name, self)
                continue
            if data is not None:
                if isinstance(data, list):
                    name = '%s[]' % name
                fields[name] = data
        return self.instance_urls(request, instance, fields)

    def get_instance_value(self, instance, name):
        try:
            value = instance.obj.__getattribute__(name)
        except Exception:
            value = getattr(self, 'instance_%s' % name, None)
            if not hasattr(value, '__call__'):
                raise
            value = partial(value, instance)
        if hasattr(value, '__call__'):
            value = value()
        return as_hex(value)

    def set_instance_value(self, instance, name, value):
        '''Set the the attribute ``name`` to ``value`` in a model ``instance``
        '''
        obj = instance.obj
        current_value = getattr(obj, name, None)
        col = self.field(name)
        if is_rel_field(col):
            try:
                rel_model = self.app.models.get(col.model)
                if isinstance(current_value, (list, set)):
                    value = tuple((rel_model.instance(v) for v in value))
                    all_ids = tuple((item.id for item in value))
                    avail = set()
                    for item in tuple(current_value):
                        item = rel_model.instance(item)
                        if item.id not in all_ids:
                            current_value.remove(item.obj)
                        else:
                            avail.add(item.id)
                    for item in value:
                        if item.id not in avail:
                            current_value.append(item.obj)
                else:
                    if value is not None:
                        value = rel_model.instance(value).obj
                        if current_value is not None:
                            current_value = rel_model.instance(current_value)
                            if self.same_instance(value, current_value):
                                return
                    setattr(obj, name, value)
            except Exception as exc:    # pragma    nocover
                self.app.logger.error(
                    'Could not replace related field %s in model '
                    '%s: %s', col.name, self, exc)
        else:
            setattr(obj, name, value)

    # ADDITIONAL PUBLIC METHODS
    def id_repr(self, request, obj, in_list=True):
        if obj:
            if in_list:
                data = {'id': as_hex(getattr(obj, self.id_field))}
            else:
                data = self.tojson(request, obj, exclude_related=True)
                data['id'] = data.pop(self.id_field)

            if self.repr_field != self.id_field:
                repr = getattr(obj, self.repr_field)
                if repr != data['id']:
                    data['repr'] = repr
            return data

    def db_model(self):
        '''Database model
        '''
        return self.app.odm()[self.name]

    def db_columns(self, columns=None):
        '''Return a list of columns available in the database table
        '''
        dbc = self._fields.load(self).db_columns
        if columns is None:
            return tuple(dbc)
        else:
            columns = self.column_fields(columns)
            return [c for c in columns if c in dbc]

    # INTERNALS
    def _same_instance(self, obj1, obj2):
        if type(obj1) == type(obj2):
            if obj1 is not None:
                for pk in class_mapper(type(obj1)).primary_key:
                    if getattr(obj1, pk.name) != getattr(obj2, pk.name):
                        return False
                return True
            else:
                return True
        return False

    def _load_fields_map(self, rest):
        '''List of column definitions
        '''
        fields = self._fields
        fields.db_columns = get_columns(self.db_model())._data
        cols = fields.db_columns.copy()

        def _set_field(field):
            if field.name in fields.hidden:
                field.hidden = True
            if is_rel_field(field) and field.field:
                fields.add_exclude(field.field)
            rest[field.name] = field

        # process input columns first
        for info in fields.include:
            col = RestField.make(info)
            if col.name not in rest:
                dbcol = cols.pop(col.name, None)
                # If a database column
                if isinstance(dbcol, Column):
                    info = column_info(col.name, dbcol)
                    info.update(col.tojson())
                    col = RestField.make(info)
                _set_field(col)

        for name, col in cols.items():
            if name not in rest:
                _set_field(RestField.make(column_info(name, col)))

        return rest

    def _related_model(self, request, model, obj, in_list):
        if isinstance(obj, list):
            return [self._related_model(request, model, d, True) for d in obj]
        else:
            return model.id_repr(request, obj, in_list)


def column_info(name, col):
    sortable = True
    filter = True
    try:
        python_type = col.type.python_type
        type = _types.get(python_type, 'string')
    except NotImplementedError:
        type = col.type.__class__.__name__.lower()
        sortable = False
        filter = False

    info = {'name': name,
            'field': col.name,
            'displayName': col.doc,
            'sortable': sortable,
            'filter': filter,
            'type': type}

    return info


@app_attribute
def odm_models(app):
    return {}


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
