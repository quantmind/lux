import uuid

from abc import ABC, abstractmethod
from copy import copy
from inspect import isclass
from contextlib import contextmanager

from pulsar.api import UnprocessableEntity, MethodNotAllowed, context

from .component import Component
from .schema import resource_name, get_schema_class
from ..utils.data import compact_dict


GET_HEAD = frozenset(('GET', 'HEAD'))
POST_PUT = frozenset(('POST', 'PUT'))


class ModelNotAvailable(Exception):
    pass


class ModelContainer(dict, Component):
    """Mapping of model identifiers to :class:`.LuxModel` objects
    """
    default_key = None

    def register(self, model, clone=True):
        '''Register a new Lux Model to the application
        '''
        if not model:
            return

        if not isinstance(model, Model):
            model = model()

        if model.uri in self:
            return self[model.uri]

        if clone:
            model = copy(model)

        model.init_app(self.app)
        if model.uri:
            self[model.uri] = model
            self.default_key = model.uri

        return model

    def get(self, name, default=None):
        if isinstance(name, Model):
            name = name.uri
        return super().get(name, default)

    def begin_session(self, **kw):
        return self[self.default_key].begin_session(**kw)

    def session(self, **kw):
        return self[self.default_key].session(**kw)


class Model(ABC, Component):
    """Base class for models

    A model has the ability to perform CRUD operations and pagination
    """
    uri = None
    """Unique resource identifier of the model, usually a url or a url path"""
    model_schema = None
    """Defines the model properties"""
    create_schema = None
    """Defines which properties are needed to create a new instance"""
    update_schema = None
    """Defines which properties can be updated"""
    query_schema = None
    """Defines which properties can be used for querying"""

    def __init__(self, uri, model_schema=None, create_schema=None,
                 update_schema=None, query_schema=None, **metadata):
        assert uri, 'model uri not available'
        self.uri = uri
        self.model_schema = self.model_schema or model_schema
        self.create_schema = self.create_schema or create_schema
        self.update_schema = self.update_schema or update_schema
        self.query_schema = self.query_schema or query_schema
        self.metadata = metadata

    def __repr__(self):
        return self.uri
    __str__ = __repr__

    # ABSTRACT METHODS
    @abstractmethod
    def session(self, request=None):
        """Return a session for aggregating a query.

        This method must return a context manager with the following methods:

        * ``add(model)``: add a model to the session
        * ``delete(model)`: delete a model
        """

    @abstractmethod
    def get_query(self, session):
        """Create a new :class:`.Query` from a session
        """

    @abstractmethod
    def create_instance(self, session, data):
        pass

    @abstractmethod
    def update_instance(self, session, instance, data):
        pass

    # SESSION CONTEXT MANAGER

    @contextmanager
    def begin_session(self, session=None, commit=False, **kw):
        if session is None:
            session = self.session(**kw)
            close = True
            commit = True
            context.stack_push('session', session)
        else:
            close = False

        try:
            yield session
            if commit:
                session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            if close:
                session.close()
                context.stack_pop('session')

    # SCHEMA METHODS

    def get_schema(self, schema=None, **kw):
        schema = schema or self.model_schema
        if not isclass(schema):
            schema = type(schema)
        schema = get_schema_class(schema.__name__)
        return schema(**kw)

    def all_schemas(self):
        if self.model_schema:
            yield self.model_schema
        if self.create_schema:
            yield self.create_schema
        if self.update_schema:
            yield self.update_schema
        if self.query_schema:
            yield self.query_schema

    def field(self, name, schema=None):
        schema = self.get_schema(schema or self.model_schema)
        return schema.fields.get(name) if schema else None

    def fields_map(self, base_fields=None, **kwargs):
        return base_fields

    # Model CRUD Responses

    def get_one_response(self, request, instance=None, schema=None):
        with self.begin_session() as session:
            if instance is None:
                instance = self.get_one(session, **request.urlargs)
            schema = self.get_schema(schema or self.model_schema)
            data = schema.dump(instance).data
        return request.json_response(data)

    def create_response(self, request, schema=None, body_schema=None):
        """Create a new instance and return a response
        """
        data, files = self.data_and_files(request)
        with self.begin_session() as session:
            model = self.create_one(session, data, body_schema)
            schema = self.get_schema(schema or self.model_schema)
            data = schema.dump(model).data
        return request.json_response(data, 201)

    def update_one_response(self, request, schema=None, body_schema=None):
        data, files = self.data_and_files(request)
        with self.begin_session() as session:
            instance = self.get_one(session, **request.urlargs)
            instance = self.update_one(session, instance, data, body_schema)
            schema = self.get_schema(schema or self.model_schema)
            data = schema.dump(instance).data
        return request.json_response(data, 200)

    def get_list_response(self, request, schema=None, query_schema=None,
                          *filters, **params):
        """Get a HTTP response for a list of model data
        """
        params.update(request.url_data)
        with self.begin_session() as session:
            query = self.query(session, *filters, **params)
            only = query.fields or None
            schema = self.get_schema(schema or self.model_schema, only=only)
            data = schema.dump(query.all(), many=True).data
        return request.json_response(data)

    def delete_one_response(self, request, instance=None):
        with self.begin_session() as session:
            if instance is None:
                instance = self.get_one(session, **request.urlargs)
            self.delete_instance(session, instance)
        request.response.status_code = 204
        return request.response

    # Model CRUD Operations

    def get_list(self, session, *filters, **kwargs):
        """Get a list of instances from positional and keyed-valued filters
        """
        query = self.query(session, *filters, **kwargs)
        return query.all()

    def paginate(self, session, limit=50, query=None):
        if query is None:
            query = self.query(session)
        while True:
            data = query.limit(limit).all()
            for obj in data:
                yield obj
            if len(data) < limit:
                break

    def get_one(self, session, *filters, **kwargs):
        query = self.query(session, *filters, **kwargs)
        return query.one()

    def create_one(self, session, data, schema=None):
        """Create a new model
        """
        schema = self.get_schema(schema or self.create_schema)
        if not schema:
            raise MethodNotAllowed
        data, errors = schema.load(data)
        if errors:
            raise self.unprocessable_entity(errors, schema)
        instance = self.create_instance(session, data)
        try:
            session.flush()
        except Exception:
            self.logger.exception('Could not create new entry')
            raise self.unprocessable_entity() from None
        return instance

    def update_one(self, session, instance, data, schema=None):
        schema = self.get_schema(schema or self.update_schema)
        if not schema:
            raise MethodNotAllowed
        data, errors = schema.load(data, partial=True)
        if errors:
            raise self.unprocessable_entity(errors, schema)
        return self.update_instance(session, instance, data)

    def delete_instance(self, session, instance):
        session.delete(instance)

    def create_uuid(self, id=None):
        if isinstance(id, uuid.UUID):
            return id
        return uuid.uuid4()

    # QUERY API
    def data_and_files(self, request):
        return request.data_and_files()

    def query(self, session, *filters, check_permission=None, load_only=None,
              query=None, **params):
        """Get a :class:`.Query` object

        :param request: WsgiRequest object
        :param session: A session for this model query
        :param filters: optional positional filters
        :param check_permission: Optional action or dictionary to check
            permission for (string or dictionary)
        :param load_only: optional list of fields to load
        :param params: key-valued filters
        """
        if query is None:
            query = self.get_query(session)
        if load_only and isinstance(load_only, str):
            load_only = (load_only,)
        if check_permission:
            fields = check_permission(session, load_only=load_only)
            query = query.load_only(*fields)
        elif load_only:
            query = query.load_only(*load_only)
        return query.filter(*filters, **params)

    def unprocessable_entity(self, errors=None, schema=None):
        error_list = []
        resource = resource_name(schema)
        if errors:
            for field, messages in errors.items():
                if isinstance(messages, str):
                    messages = (messages,)
                for message in messages:
                    error_list.append(
                        compact_dict(
                            field=field, code=message, resource=resource
                        )
                    )
        return UnprocessableEntity(error_list)

    def field_errors(self, fields, message=None):
        message = message or 'not available'
        return dict(((name, message) for name in fields))
