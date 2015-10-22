from pulsar import PermissionDenied

from .models import RestModel


__all__ = ['ModelMixin', 'ColumnPermissionsMixin']


class ModelMixin:
    '''Mixin for accessing Rest models from the application object
    '''
    RestModel = RestModel
    _model = None

    def set_model(self, model):
        '''Set the default model for this mixin
        '''
        assert model
        if isinstance(model, str):
            model = self.RestModel(model)
        self._model = model

    def model(self, app, model=None):
        '''Return a :class:`.RestModel` model registered with ``app``.

        If ``model`` is not available, uses the :attr:`._model`
        attribute.
        '''
        app = app.app
        rest_models = getattr(app, '_rest_models', None)
        if rest_models is None:
            rest_models = {}
            app._rest_models = rest_models

        if not model:
            if hasattr(self._model, '__call__'):
                self._model = self._model()
            model = self._model

        assert model, 'No model specified'

        if model.url not in rest_models:
            rest_models[model.url] = model.add_to_app(app)
        return rest_models[model.url]


class ColumnPermissionsMixin(ModelMixin):
    '''Mixin for managing model permissions at column (field) level

    This mixin can be used by any class.
    '''
    def columns(self, request):
        '''Returns the column list for this mixin.
        By default it returns the columns given by the model
        '''
        return self.model(request.app).columns(request)

    def column_fields(self, columns, field=None):
        '''Return a list column fields from the list of columns object
        '''
        field = field or 'field'
        fields = set()
        for c in columns:
            value = c[field]
            if isinstance(value, (tuple, list)):
                fields.update(value)
            else:
                fields.add(value)
        return tuple(fields)

    def has_permission_for_column(self, request, column, level):
        """
        Checks permission for a column in the model

        :param request:     request object
        :param column:      column name
        :param level:       requested access level
        :return:            True iff user has permission
        """
        backend = request.cache.auth_backend
        model = self.model(request.app)
        permission_name = "{}:{}".format(model.name, column['name'])
        return backend.has_permission(request, permission_name, level)

    def column_permissions(self, request, level):
        """
        Gets whether the user has the quested access level on
        each column in the model.

        Results are cached for future function calls

        :param request:     request object
        :param level:       access level
        :return:            dict, with column names as keys,
                            Booleans as values
        """
        model = self.model(request.app)
        ret = None
        cache = request.cache
        if 'model_permissions' not in cache:
            cache.model_permissions = {}
        if model.name not in cache.model_permissions:
            cache.model_permissions[model.name] = {}
        elif level in cache.model_permissions[model.name]:
            ret = cache.model_permissions[model.name][level]

        if not ret:
            perm = self.has_permission_for_column
            columns = self.columns(request)
            ret = {
                col['name']: perm(request, col, level) for
                col in columns
                }
            cache.model_permissions[model.name][level] = ret
        return ret

    def columns_with_permission(self, request, level):
        """
        Returns a frozenset with the columns the user has the requested
        level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        columns = self.columns(request)
        perms = self.column_permissions(request, level)
        return tuple((col for col in columns if perms.get(col['name'])))

    def columns_without_permission(self, request, level):
        """
        Returns a frozenset with the columns the user does not have
        the requested level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        columns = self.columns(request)
        perms = self.column_permissions(request, level)
        return tuple((col for col in columns if not perms.get(col['name'])))

    def check_model_permission(self, request, level, model=None):
        """
        Checks whether the user has the requested level of access to
        the model, raising PermissionDenied if not

        :param request:     request object
        :param level:       access level
        :raise:             PermissionDenied
        """
        model = model or self.model(request.app)
        backend = request.cache.auth_backend
        if not backend.has_permission(request, model.name, level):
            raise PermissionDenied
