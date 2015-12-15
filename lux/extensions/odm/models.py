import json
from datetime import date, datetime
from enum import Enum

import pytz

from sqlalchemy import Column, desc, String
from sqlalchemy.orm import class_mapper, load_only
from sqlalchemy.sql.expression import func, cast

from pulsar.utils.html import nicename

from odm.utils import get_columns

from lux.extensions import rest


def is_same_model(model1, model2):
    if type(model1) == type(model2):
        if model1 is not None:
            pkname = class_mapper(type(model1)).primary_key[0].name
            return getattr(model1, pkname) == getattr(model2, pkname)
        else:
            return True
    return False


class RestColumn(rest.RestColumn):
    pass


class RestModel(rest.RestModel):
    '''A rest model based on SqlAlchemy ORM
    '''
    _db_columns = None
    _rest_columns = None

    def session(self, request):
        '''Obtain a session
        '''
        return request.app.odm().begin()

    def query(self, request, session, *filters):
        """
        Returns a query object for the model.

        The loading of columns the user does not have read
        access to is deferred. This is only a performance enhancement.

        :param request:     request object
        :param session:     SQLAlchemy session
        :return:            query object
        """
        entities = self.columns_with_permission(request, 'read')
        db_model = self.db_model()
        db_columns = self.db_columns(self.column_fields(entities))
        query = session.query(db_model).options(load_only(*db_columns))
        if filters:
            query = query.filter(*filters)
        return query

    def serialise_model(self, request, data, **kw):
        """
        Makes a model instance JSON-friendly. Removes fields that the
        user does not have read access to.

        :param request:     request object
        :param data:        data
        :param kw:          not used
        :return:            dict
        """
        exclude = self.columns_without_permission(request, 'read')
        exclude = self.column_fields(exclude, 'name')
        return self.tojson(request, data, exclude=exclude)

    def meta(self, request, *filters, exclude=None):
        meta = super().meta(request, exclude=exclude)
        odm = request.app.odm()
        with odm.begin() as session:
            query = self.query(request, session, *filters)
            meta['total'] = query.count()
        return meta

    def load_related(self,  instance):
        for column in self._rest_columns.values():
            if isinstance(column, ModelColumn):
                getattr(instance, column.name)

    def db_model(self):
        '''Database model
        '''
        assert self._app, 'ODM Rest Model not loaded'
        return self._app.odm()[self.name]

    def db_columns(self, columns=None):
        '''Return a list of columns available in the database table
        '''
        assert self._db_columns, 'ODM Rest Model not loaded'
        if columns is None:
            return tuple(self._db_columns.keys())
        else:
            return [c for c in columns if c in self._db_columns]

    def add_related_column(self, name, model, field=None, **kw):
        '''Add a related column to the model
        '''
        assert not self._loaded, 'already loaded'
        if field:
            self._exclude.add(field)
        column = ModelColumn(name, model, field=field, **kw)
        cols = list(self._columns or ())
        cols.append(column)
        self._columns = cols

    def set_model_attribute(self, instance, name, value):
        '''Set the the attribute ``name`` to ``value`` in a model ``instance``
        '''
        current_value = getattr(instance, name, None)
        col = self._rest_columns.get(name)
        if isinstance(col, ModelColumn):
            if isinstance(current_value, (list, set)):
                if not isinstance(value, (list, tuple, set)):
                    raise TypeError('list or tuple required')
                relmodel = col.model(self._app)
                idfield = relmodel.id_field
                all = set((getattr(v, idfield) for v in value))
                avail = set()
                for item in tuple(current_value):
                    pkey = getattr(item, idfield)
                    if pkey not in all:
                        current_value.remove(item)
                    else:
                        avail.add(pkey)
                for item in value:
                    pkey = getattr(item, idfield)
                    if pkey not in avail:
                        current_value.append(item)
            elif not is_same_model(current_value, value):
                setattr(instance, name, value)
        else:
            setattr(instance, name, value)

    def tojson(self, request, obj, exclude=None):
        '''Override the method from the base class.

        It uses sqlalchemy model information about columns
        '''
        exclude = set(exclude or ())
        exclude.update(self._exclude)
        columns = self.columns(request.app)

        fields = {}
        for col in columns:
            name = col['name']
            restcol = self._rest_columns[name]
            if name in exclude:
                continue
            try:
                data = obj.__getattribute__(name)
                if hasattr(data, '__call__'):
                    data = data()
                if isinstance(data, date):
                    if isinstance(data, datetime) and not data.tzinfo:
                        data = pytz.utc.localize(data)
                    data = data.isoformat()
                elif isinstance(data, Enum):
                    data = data.name
                elif isinstance(restcol, ModelColumn):
                    related = restcol.model(request.app)
                    data = self._related_model(request, related, data)
                else:   # Test Json
                    json.dumps(data)
            except TypeError:
                try:
                    data = str(data)
                except Exception:
                    continue
            if data is not None:
                if isinstance(data, list):
                    name = '%s[]' % name
                fields[name] = data
        # a json-encodable dict
        return fields

    def id_repr(self, request, obj):
        if obj:
            data = {'id': getattr(obj, self.id_field)}
            if self.repr_field != self.id_field:
                repr = getattr(obj, self.repr_field)
                if repr != data['id']:
                    data['repr'] = repr
            return data

    def create_model(self, request, data, session=None):
        odm = request.app.odm()
        db_model = self.db_model()
        with odm.begin(session=session) as session:
            instance = db_model()
            session.add(instance)
            for name, value in data.items():
                self.set_model_attribute(instance, name, value)
            session.flush()
            self.load_related(instance)
        return instance

    def update_model(self, request, instance, data):
        self.columns(request)  # TODO, columns need to be loaded
        odm = request.app.odm()
        session = odm.session_from_object(instance)
        with odm.begin(session=session) as session:
            session.add(instance)
            for name, value in data.items():
                self.set_model_attribute(instance, name, value)
        return instance

    def delete_model(self, request, instance):
        odm = request.app.odm()
        session = odm.session_from_object(instance)
        with odm.begin(session=session) as session:
            session.delete(instance)

    def _load_columns(self, app):
        '''List of column definitions
        '''
        model = self.db_model()
        self._db_columns = get_columns(model)
        self._rest_columns = {}
        input_columns = self._columns or []
        cols = self._db_columns._data.copy()
        columns = []

        for info in input_columns:
            col = RestColumn.make(info)
            if col.name not in self._rest_columns:
                dbcol = cols.pop(col.name, None)
                # If a database column
                if isinstance(dbcol, Column):
                    info = column_info(col.name, dbcol)
                    info.update(col.as_dict(defaults=False))
                else:
                    info = col.as_dict()
                self._append_col(col, columns, info)

        for name, col in cols.items():
            if name not in self._rest_columns:
                self._append_col(col, columns, column_info(name, col))

        return columns

    def _append_col(self, col, columns, info):
        name = info['name']
        self._rest_columns[name] = col
        if name in self._hidden:
            info['hidden'] = True
        columns.append(info)

    def _related_model(self, request, model, obj):
        if isinstance(obj, list):
            return [self._related_model(request, model, d) for d in obj]
        else:
            return model.id_repr(request, obj)

    def _do_filter(self, request, query, field, op, value):
        """
        Applies filter conditions to a query.

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


        :param request:     request object
        :param query:       query object
        :param field:       field name
        :param op:          'eq', 'ne', 'gt', 'lt', 'ge', 'le' or 'search'
        :param value:       comparison value, string or list/tuple
        :return:
        """
        app = request.app
        odm = app.odm()
        field = getattr(odm[self.name], field)
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
        return query

    def _do_sortby(self, request, query, entry, direction):
        columns = self.db_columns()
        if entry in columns:
            if direction == 'desc':
                entry = desc(entry)
            return query.order_by(entry)
        return query


class ModelMixin(rest.ModelMixin):
    RestModel = RestModel


class ModelColumn(RestColumn, ModelMixin):
    '''A Column based on another model
    '''
    def __init__(self, name, model, **kwargs):
        super().__init__(name, **kwargs)
        self.set_model(model)


def column_info(name, col):
    sortable = True
    filter = True
    try:
        python_type = col.type.python_type
        type = _types.get(python_type, 'string')
        remote_type = python_type.__name__.lower()
    except NotImplementedError:
        type = col.type.__class__.__name__.lower()
        remote_type = type
        sortable = False
        filter = False

    info = {'name': name,
            'field': col.name,
            'displayName': col.doc or nicename(name),
            'sortable': sortable,
            'filter': filter,
            'type': type,
            'remoteType': remote_type}

    return info


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
