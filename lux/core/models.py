from copy import copy
from inspect import isgenerator

from pulsar import ImproperlyConfigured
from pulsar.utils.log import lazymethod


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
    identifier = None
    _app = None

    @property
    def app(self):
        if not self._app:
            raise ImproperlyConfigured('Model "%s" not registered' % self)
        return self._app

    @lazymethod
    def columns(self):
        return self._load_columns()

    def register(self, app):
        self._app = app

    def serialise(self, request, data, **kw):
        """Serialise a model or a collection of models
        """
        if isinstance(data, list) or isgenerator(data):
            kw['in_list'] = True
            return [self.serialise_model(request, o, **kw) for o in data]
        else:
            return self.serialise_model(request, data)

    def set_model_attribute(self, instance, name, value):
        '''Set the the attribute ``name`` to ``value`` in a model ``instance``
        '''
        setattr(instance, name, value)

    def serialise_model(self, request, data, **kw):
        """Serialise on model
        """
        return self.tojson(request, data, **kw)

    def validate_fields(self, request, instance, data):
        """Validate fields values
        """
        pass

    def get_instance(self, request, *args, **kwargs):
        """Retrieve an instance of this model
        """
        raise NotImplementedError

    def get_list(self, request, *args, **kwargs):
        """Retrieve a list of instances of this model
        """
        raise NotImplementedError

    def tojson(self, request, instance, in_list=False,
               exclude=None, decoder=None):
        '''Convert a model ``object`` into a JSON serializable
        dictionary
        '''
        raise NotImplementedError

    def session(self, request):
        '''Return a session for aggregating a query.
        The retunred object should be context manager and support the query
        method.
        '''
        raise NotImplementedError

    def query(self, request, session, *filters):
        '''Manipulate a query if needed
        '''
        raise NotImplementedError

    def create_model(self, request, data, session=None):
        """Create a new model form data
        """
        raise NotImplementedError

    def context(self, request, instance, context):
        """Add context to an instance context

        :param request: WSGI request
        :param instance: an instance of this model
        :param context: context dictionary
        :return:
        """

    def same_instance(self, instance1, instance2):
        """Compare two instances for equality
        """
        return instance1 == instance2

    def _load_columns(self):
        raise NotImplementedError
