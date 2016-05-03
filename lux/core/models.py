from copy import copy

from pulsar import ImproperlyConfigured
from pulsar.utils.log import lazymethod


class ModelContainer(dict):

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

    def set_model_attribute(self, instance, name, value):
        '''Set the the attribute ``name`` to ``value`` in a model ``instance``
        '''
        setattr(instance, name, value)

    def serialise_model(self, request, data, **kw):
        """Serialise on model
        """
        return self.tojson(request, data, **kw)

    def validate_fields(self, request, data):
        """Validate fields values
        """
        pass

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

    def _load_columns(self):
        raise NotImplementedError
