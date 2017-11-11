import uuid

from abc import ABC, abstractmethod
from copy import copy
from inspect import isclass

from pulsar.api import UnprocessableEntity, MethodNotAllowed

from lux.utils.crypt import as_hex

from .component import Component, app_cache
from .schema import resource_name
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

    def session(self, request=None):
        return self[self.default_key].session(request)


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
    def __call__(self, data, session):
        pass

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

    # SCHEMA METHODS

    def get_schema(self, schema, only=None):
        if isclass(schema):
            if only:
                return schema(app=self.app, only=only)
            schemas = app_schemas(self.app)
            name = schema.__name__
            if name not in schemas:
                schemas[name] = schema(app=self.app)
            return schemas[name]
        elif only:
            return type(schema)(app=self.app, only=only)
        return schema

    def all_schemas(self):
        if self.model_schema:
            yield self.get_schema(self.model_schema)
        if self.create_schema:
            yield self.get_schema(self.create_schema)
        if self.update_schema:
            yield self.get_schema(self.update_schema)
        if self.query_schema:
            yield self.get_schema(self.query_schema)

    def field(self, name, schema=None):
        schema = self.get_schema(schema or self.model_schema)
        return schema.fields.get(name) if schema else None

    def fields_map(self, base_fields=None, **kwargs):
        return base_fields

    # Model CRUD Responses

    def get_one_response(self, request, instance=None, schema=None):
        with self.session(request) as session:
            if instance is None:
                instance = self.get_one(session, **request.urlargs)
            schema = self.get_schema(schema or self.model_schema)
            data = schema.dump(instance).data
        return request.json_response(data)

    def create_response(self, request, schema=None):
        """Create a new instance and return a response
        """
        data, files = request.data_and_files()
        with self.session(request) as session:
            model = self.create_one(session, data, schema)
            schema = self.get_schema(self.model_schema)
            data = schema.dump(model).data
        return request.json_response(data, 201)

    def update_one_response(self, request, schema=None):
        data, files = request.data_and_files()
        with self.session(request) as session:
            model = self.update_one(session, data, schema)
            schema = self.get_schema(self.model_schema)
            data = schema.dump(model).data
        return request.json_response(data, 201)

    def get_list_response(self, request, *filters, **params):
        """Get a HTTP response for a list of model data
        """
        params.update(request.url_data)
        with self.session(request) as session:
            query = self.query(session, *filters, **params)
            only = query.fields or None
            schema = self.get_schema(self.model_schema, only=only)
            data = schema.dump(query.all(), many=True).data
        return request.json_response(data)

    def delete_one_response(self, request, instance=None):
        with self.session(request) as session:
            if instance is None:
                instance = self.get_one(session, **request.urlargs)
            session.delete(instance)
        request.response.status_code = 204
        return request.response

    # CRUD Methods

    def get_list(self, session, *filters, **kwargs):
        """Get a list of instances from positional and keyed-valued filters
        """
        query = self.query(session, *filters, **kwargs)
        return query.all()

    # Model CRUD Operations
    def get_one(self, session, *filters, **kwargs):
        query = self.query(session, *filters, **kwargs)
        return query.one()

    def create_one(self, session, data, schema=None):
        schema = self.get_schema(schema or self.create_schema)
        if not schema:
            raise MethodNotAllowed
        model, errors = schema.load(data, session=session)
        if errors:
            raise self.unprocessable_entity(errors, schema)
        session.flush()
        return model

    def update_one(self, session, data, schema=None):
        schema = self.get_schema(schema or self.update_schema)
        if not schema:
            raise MethodNotAllowed
        model, errors = schema.load(data, session=session, partial=True)
        if errors:
            raise self.unprocessable_entity(errors, schema)
        return model

    def create_uuid(self, id=None):
        if isinstance(id, uuid.UUID):
            return id
        return uuid.uuid4()

    # QUERY API
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

    # CRUD API
    def create_model(self, request, instance=None, data=None, session=None):
        """Create a model ``instance``"""
        if instance is None:
            instance = self.instance()
        return self.update_model(request, instance, data,
                                 session=session, flush=True)

    def update_model(self, request, instance, data, session=None, flush=False):
        """Update a model ``instance``"""
        if data is None:
            data = {}
        instance = self.instance(instance)
        with self.session(request, session=session) as session:
            session.add(instance.obj)
            for name, value in data.items():
                if instance.has(name):
                    instance.set(name, value)
            if flush:
                session.flush()
        return instance

    def delete_model(self, request, instance, session=None):
        """Delete a model ``instance``"""
        instance = self.instance(instance)
        with self.session(request, session=session) as session:
            session.delete(instance.obj)

    def set_instance_value(self, instance, name, value):
        setattr(instance.obj, name, value)

    def get_instance_value(self, instance, name):
        return as_hex(getattr(instance.obj, name, None))

    def value_from_data(self, name, data, instance=None):
        if name in data:
            return data[name]
        elif instance is not None:
            return self.get_instance_value(self.instance(instance), name)

    def same_instance(self, instance1, instance2):
        if instance1 is not None and instance2 is not None:
            obj1 = self.instance(instance1).obj
            obj2 = self.instance(instance2).obj
            return self._same_instance(obj1, obj2)
        return False

    # INTERNALS
    def _same_instance(self, obj1, obj2):
        return obj1 == obj2

    def load_only_fields(self, load_only=None):
        """Generator of field names"""
        for field in self.fields():
            if load_only is None or field in load_only:
                yield field

    def context(self, request, instance, context):
        """Add context to an instance context

        :param request: WSGI request
        :param instance: an instance of this model
        :param context: context dictionary
        :return:
        """

    def validate_fields(self, request, instance, data):
        """Validate fields values
        """
        pass

    def unprocessable_entity(self, errors, schema=None):
        error_list = []
        resource = resource_name(schema)
        for field, messages in errors.items():
            for message in messages:
                error_list.append(
                    compact_dict(field=field, code=message, resource=resource)
                )
        return UnprocessableEntity(error_list)


@app_cache
def app_schemas(app):
    return {}
