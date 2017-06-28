from datetime import date, datetime
from functools import partial

from sqlalchemy import desc, String
from sqlalchemy.orm import class_mapper, load_only
from sqlalchemy.sql.expression import func, cast
from sqlalchemy.exc import DataError, StatementError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.dialects import postgresql

from marshmallow_sqlalchemy import ModelConverter

from pulsar.api import Http404
from pulsar.utils.log import lazyproperty

from odm.mapper import object_session

from lux.core import app_attribute
from lux.utils.crypt import as_hex
from lux import models
from lux.models import fields

from .fields import get_primary_keys


MissingObjectError = (DataError, NoResultFound, StatementError)
model_converter = ModelConverter(models.Schema)
property2field = model_converter.property2field
column2field = model_converter.column2field

model_converter.SQLA_TYPE_MAPPING = model_converter.SQLA_TYPE_MAPPING.copy()
model_converter.SQLA_TYPE_MAPPING[postgresql.UUID] = fields.UUID


class Query(models.Query):
    """ODM based query"""

    def __init__(self, model, session):
        self.sql_query = session.query(model.db_model)
        self.joins = set()
        super().__init__(model, session)

    def count(self):
        return self._query().count()

    def one(self):
        query = self._query()
        try:
            return query.one()
        except MissingObjectError:
            raise Http404
        except MultipleResultsFound:
            self.logger.error('%s - Multiple result found for "%s". '
                              'Returning the first' %
                              (self.request, self.model))
            return query.first()

    def all(self):
        return self._query().all()

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
        query = self.sql_query
        model = field.parent.model
        db_model = model.db_model
        field = getattr(db_model, field.name, None)

        if not field and False:
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
                odm = app.odm()
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


class Model(models.Model):
    '''A rest model based on SqlAlchemy ORM
    '''
    property2field = property2field
    object_session = object_session
    primary_keys = None

    @property
    def db_name(self):
        """name of the database model
        """
        name = self.metadata.get('db_name')
        if not name:
            name = self.uri.split('/')[-1]
            name = models.inflect.singular_noun(name) or name
            self.metadata['db_name'] = name
        return name

    @property
    def db_model(self):
        """Database model class
        """
        if self.app:
            return self.app.odm()[self.db_name]

    @lazyproperty
    def primary_keys(self):
        return get_primary_keys(self.db_model)

    def __call__(self, data, session):
        db_model = self.db_model
        filters = {pk.key: data.get(pk.key) for pk in self.primary_keys}
        instance = None
        if None not in filters.values():
            try:
                instance = self.get_one(session, **filters)
            except Http404:
                pass
        if instance is not None:
            for key, value in data.items():
                setattr(instance, key, value)
        else:
            instance = db_model(**data)
        session.add(instance)
        return instance

    def session(self, request=None):
        return self.app.odm().begin(request=request)

    def get_query(self, session):
        return Query(self, session)

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

    def fields_map(self, include_fk=False, fields=None,
                   exclude=None, base_fields=None, dict_cls=dict):
        '''List of column definitions
        '''
        result = dict_cls()
        base_fields = base_fields or {}
        db_name = self.db_name
        fields_map = odm_fields_map(self.app)
        db_columns = fields_map.get(db_name)

        if db_columns is None:
            db_columns = {}
            fields_map[db_name] = db_columns

        for column in self.db_model.__mapper__.iterate_properties:
            if _should_exclude_field(column, fields=fields, exclude=exclude):
                continue
            if hasattr(column, 'columns'):
                if not include_fk:
                    # Only skip a column if there is no overridden column
                    # which does not have a Foreign Key.
                    for col in column.columns:
                        if not col.foreign_keys:
                            break
                    else:
                        continue
            field = base_fields.get(column.key) or db_columns.get(column.key)
            if not field:
                field = self.property2field(column)
                if field:
                    db_columns[column.key] = field

            if field:
                result[column.key] = field
        return result


@app_attribute
def odm_fields_map(app):
    return {}


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


def _should_exclude_field(column, fields=None, exclude=None):
    if fields and column.key not in fields:
        return True
    if exclude and column.key in exclude:
        return True
    return False


_types = {int: 'integer',
          bool: 'boolean',
          date: 'date',
          datetime: 'datetime'}
