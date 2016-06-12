from copy import copy

from pulsar import ImproperlyConfigured, Http404, PermissionDenied


class ModelContainer(dict):
    """Mapping of model identifiers to :class:`.LuxModel` objects
    """
    def __init__(self, app):
        super().__init__()
        self._app = app

    def register(self, model):
        '''Register a new Lux Model to the application
        '''
        if not isinstance(model, LuxModel):
            model = model()

        if model.identifier in self:
            return self[model.identifier]

        model = copy(model)
        model.register(self._app)
        if model.identifier:
            self[model.identifier] = model

        return model

    def get(self, name, default=None):
        if isinstance(name, LuxModel):
            name = name.identifier
        return super().get(name, default)


class LuxModel:
    """Base class for models
    """
    name = None
    identifier = None
    _app = None

    @property
    def app(self):
        if not self._app:
            raise ImproperlyConfigured('Model "%s" not registered' % self)
        return self._app

    # ABSTRACT METHODS
    def session(self, session=None):
        '''Return a session for aggregating a query.

        The returned object should be context manager and support the query
        method.
        '''
        raise NotImplementedError

    def get_query(self, session):
        '''Create a new :class:`.Query` from a session
        '''
        raise NotImplementedError

    def tojson(self, request, instance, **kw):
        """Convert a ``instance`` into a JSON serialisable dictionary
        """
        raise NotImplementedError

    def create_instance(self):
        """Create the underlying instance for this model
        """
        raise NotImplementedError

    def fields(self):
        """Return a Mapping name-Field of all fields in this model
        """
        raise NotImplementedError

    def field(self, name):
        """Get the field object for field ``name``
        """
        return self.fields().get(name)

    # API
    def instance(self, o=None, fields=None):
        """Return a :class:`.ModelInstance`

        :param o: None, a raw instance or a :class:`.ModelInstance
        :param fields: optional list of fields to include in the instance
        """
        """Create a new :class:`.ModelInstance`
            """
        if isinstance(o, ModelInstance):
            return o
        if o is None:
            o = self.create_instance()
        return ModelInstance.create(self, o, fields)

    def query(self, request, session, *filters, check_permission=None,
              load_only=None, **params):
        """Get a :class:`.Query` object

        :param request: WsgiRequest object
        :param session: A session for this model query
        :param filters: optional positional filters
        :param check_permission: Optional action or dictionary to check
            permission for (string or dictionary)
        :param load_only: optional list of fields to load
        :param params: key-valued filters
        """
        query = self.get_query(session)
        if check_permission:
            fields = self.fields_with_permission(request, check_permission,
                                                 load_only)
            query = query.load_only(*fields)
        elif load_only:
            query = query.load_only(*load_only)
        return query.filter(*filters, **params)

    def get_instance(self, request, *args, session=None, **kwargs):
        if not args and not kwargs:  # pragma    nocover
            raise Http404
        with self.session(request, session=session) as session:
            query = self.query(request, session, *args, **kwargs)
            return query.one()

    def create_model(self, request, instance, data, session=None):
        """Create a model ``instance``"""
        return self.update_model(request, instance, data,
                                 session=session, flush=True)

    def update_model(self, request, instance, data, session=None, flush=False):
        """Update a model ``instance``"""
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
        with self.session(request, session=session) as session:
            session.delete(instance.obj)

    def set_instance_value(self, instance, name, value):
        setattr(instance.obj, name, value)

    def get_instance_value(self, instance, name):
        return getattr(instance.obj, name, None)

    def check_permission(self, request, action, *args):
        """
        Checks whether the user has the requested level of access to
        the model, raising PermissionDenied if not

        :param request:     request object
        :param action:      action to check permission for
        :param args:        additional namespaces for resource
        :raise:             PermissionDenied
        """
        resource = self.name
        if args:
            resource = '%s:%s' % (resource, ':'.join(args))
        backend = request.cache.auth_backend
        if not backend.has_permission(request, resource, action):
            raise PermissionDenied

    def has_permission_for_field(self, request, field_name, action):
        try:
            self.check_permission(request, action, field_name)
            return True
        except PermissionDenied:
            return False

    def fields_with_permission(self, request, action, load_only=None):
        """Return a tuple of fields with valid permissions for ``action``

        If the user cannot perform ``action`` on any field this method should
        raise PermissionDenied
        """
        action, args = permission_args(action)
        self.check_permission(request, action, *args)
        fields = self.load_only_fields(load_only)
        perms = self.permissions(request, action)
        return tuple((field for field in fields if perms.get(field)))

    def permissions(self, request, action, *args):
        """
        Gets whether the user has the quested access level on
        each field in the model.

        Results are cached for future function calls

        :param request:     request object
        :param action:      access level
        :return:            dict, with column names as keys,
                            Booleans as values
        """
        ret = None
        cache = request.cache
        if 'model_permissions' not in cache:
            cache.model_permissions = {}
        if self.name not in cache.model_permissions:
            cache.model_permissions[self.name] = {}
        elif action in cache.model_permissions[self.name]:
            ret = cache.model_permissions[self.name][action]

        if not ret:
            perm = self.has_permission_for_field
            ret = {name: perm(request, name, action) for name in self.fields()}
            cache.model_permissions[self.name][action] = ret
        return ret

    # INTERNALS
    def register(self, app):
        self._app = app

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


class ModelInstance:

    def __init__(self, model, obj, fields=None):
        self.model = model
        self.obj = obj
        self.fields = fields
        obj.model_instance = self

    @property
    def id(self):
        return self.get(self.model.id_field)

    def __repr__(self):
        return repr(self.obj)

    def __str__(self):
        return str(self.obj)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def create(cls, model, obj, fields=None):
        if hasattr(obj, 'model_instance'):
            return obj.model_instance
        return cls(model, obj, fields)

    def has(self, field):
        return self.fields is None or field in self.fields

    def set(self, name, value):
        self.model.set_instance_value(self, name, value)

    def get(self, name):
        return self.model.get_instance_value(self, name)


class Query:
    "Interface for a Query"

    def __init__(self, model, session=None):
        self.model = model
        self.fields = None

    @property
    def name(self):
        return self.model.name

    @property
    def app(self):
        return self.model.app

    def one(self):
        raise NotImplementedError

    def all(self):
        """Aggregate results of this query.

        :return: an iterable over :class:`.ModelInstance`"""
        raise NotImplementedError

    def count(self):
        raise NotImplementedError

    def limit(self, limit):
        raise NotImplementedError

    def offset(self, offset):
        raise NotImplementedError

    def sortby_field(self, entry, direction):
        raise NotImplementedError

    def filter_args(self, *args):
        raise NotImplementedError

    def filter_field(self, field, op, value):
        raise NotImplementedError

    def search(self, search):
        return self

    def load_only(self, *fields):
        if self.fields is None:
            self.fields = set(fields)
        else:
            self.fields = self.fields.intersection(fields)
        return self

    def filter(self, *filters, search=None, **params):
        if filters:
            self.filter_args(filters)

        fields = self.model.fields()

        for key, value in params.items():
            bits = key.split(':')
            field = bits[0]
            if field in fields:
                op = bits[1] if len(bits) == 2 else 'eq'
                field = fields[field].field
                if isinstance(field, str):
                    self.filter_field(field, op, value)

        if search:
            self.search(search)

        return self

    def sortby(self, sortby=None):
        if sortby:
            if not isinstance(sortby, list):
                sortby = (sortby,)
            for entry in sortby:
                direction = None
                if ':' in entry:
                    entry, direction = entry.split(':')
                self.sortby_field(entry, direction)
        return self

    def tojson(self, request, **kw):
        """Convert to a JSON serializable list

        :return: a JSON serialisable list of model objects
        """
        model = self.model
        kw['in_list'] = True
        return [model.tojson(request, o, **kw) for o in self.all()]


def permission_args(action):
    args = ()
    if isinstance(action, dict):
        args = action.get('args', args)
        action = action.get('action', 'read')
    return action, args
