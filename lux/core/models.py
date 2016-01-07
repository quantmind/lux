from pulsar import ImproperlyConfigured


__all__ = ['LuxModel']


class ModelContainer:

    def __init__(self, app):
        self.app = app
        self.models = {}

    def __repr__(self):
        return repr(self._models)
    __str__ = __repr__

    def register(self, model):
        '''Register a new Lux Model to the application
        '''
        assert isinstance(model, LuxModel), ('An instance of a lux model '
                                             'is required')
        if model.identifier in self.models:
            raise ImproperlyConfigured('Model %s already registered' %
                                       model.identifier)
        if model.identifier:
            self.models[model.identifier] = model

    def get(self, identifier):
        self.models.get(identifier)


class LuxModel:
    identifier = None
