

def register_applications(stores, applications, **params):
    '''A higher level registration method for group of models located
    on application modules.

    It uses the :meth:`model_iterator` method to iterate
    through all :class:`.Model` available in ``applications``
    and :meth:`register` them.

    :parameter applications: A String or a list of strings representing
        python dotted paths where models are implemented. Can also be
        a module or a list of modules.
    :parameter models: Optional list of models to include. If not provided
        all models found in *applications* will be included.
    :parameter stores: optional dictionary which map a model or an
        application to a store
        :ref:`connection string <connection-string>`.
    :rtype: A list of registered :class:`.Model`.

    For example::


        register_applications('mylib.myapp')
        register_applications(['mylib.myapp', 'another.path'])
        register_applications(pythonmodule)
        register_applications(['mylib.myapp', pythonmodule])

    '''
    return list(_register_applications(stores, applications,  **params))


def valid_model(model):
    if isinstance(model, tuple(ModelTypes)):
        return not model._meta.abstract
    return False


def models_from_model(model, include_related=False, exclude=None):
    '''Generator of all model in model.

    :param model: a :class:`.Model`
    :param include_related: if ``True`` al related models to ``model``
        are included
    :param exclude: optional set of models to exclude
    '''
    if exclude is None:
        exclude = set()
    if valid_model(model) and model not in exclude:
        exclude.add(model)
        yield model
        if include_related:
            for column in model._meta.dfields.values():
                for fk in column.foreign_keys:
                    for model in (fk.column.table,):
                        for m in models_from_model(
                                model, include_related=include_related,
                                exclude=exclude):
                            yield m


def model_iterator(application, include_related=True, exclude=None):
    '''A generator of :class:`.Model` classes found in *application*.

    :parameter application: A python dotted path or an iterable over
        python dotted-paths where models are defined.

    Only models defined in these paths are considered.
    '''
    if exclude is None:
        exclude = set()
    if ismodule(application) or isinstance(application, str):
        if ismodule(application):
            mod, application = application, application.__name__
        else:
            try:
                mod = import_module(application)
            except ImportError:
                # the module is not there
                mod = None
        if mod:
            label = application.split('.')[-1]
            try:
                mod_models = import_module('.models', application)
            except ImportError:
                mod_models = mod
            label = getattr(mod_models, 'app_label', label)
            models = set()
            for name in dir(mod_models):
                value = getattr(mod_models, name)
                for model in models_from_model(
                        value, include_related=include_related,
                        exclude=exclude):
                    if (model._meta.app_label == label and
                            model not in models):
                        models.add(model)
                        yield model
    else:
        for app in application:
            for m in model_iterator(app, include_related=include_related,
                                    exclude=exclude):
                yield m


def _register_applications(stores, applications, **params):
    registered_models = set()

    for model in model_iterator(applications):
        name = str(model._meta)
        if models and name not in models:
            continue
        if name not in stores:
            name = model._meta.app_label
        kwargs = stores.get(name, self._default_store)
        if not isinstance(kwargs, dict):
            kwargs = {'backend': kwargs}
        else:
            kwargs = kwargs.copy()
        if self.register(model, include_related=False, **kwargs):
            yield model
