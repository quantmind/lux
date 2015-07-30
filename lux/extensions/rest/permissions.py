from pulsar import PermissionDenied


__all__ = ['ColumnPermissionsMixin']


class ColumnPermissionsMixin:
    '''Mixin for managing model permissions at column (field) level

    This mixin can be used by any class.
    '''
    def has_permission_for_column(self, request, model, column, level):
        """
        Checks permission for a column in the model

        :param request:     request object
        :param column:      column name
        :param level:       requested access level
        :return:            True iff user has permission
        """
        backend = request.cache.auth_backend
        permission_name = "{}:{}".format(model.name, column['name'])
        return backend.has_permission(request, permission_name, level)

    def column_permissions(self, request, model, level):
        """
        Gets whether the user has the quested access level on
        each column in the model.

        Results are cached for future function calls

        :param request:     request object
        :param level:       access level
        :return:            dict, with column names as keys,
                            Booleans as values
        """
        ret = None
        cache = request.cache
        if 'model_permissions' not in request.cache:
            cache.model_permissions = {}
        if model.name not in cache.model_permissions:
            cache.model_permissions[model.name] = {}
        elif level in cache.model_permissions[model.name]:
            ret = cache.model_permissions[model.name][level]

        if not ret:
            perm = self.has_permission_for_column
            columns = model.columns(request)
            ret = {
                col['name']: perm(request, model, col, level) for
                col in columns
                }
            cache.model_permissions[model.name][level] = ret
        return ret

    def columns_with_permission(self, request, model, level):
        """
        Returns a frozenset with the columns the user has the requested
        level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        perms = self.column_permissions(request, model, level)
        ret = frozenset(k for k, v in perms.items() if v)
        return ret

    def columns_without_permission(self, request, model, level):
        """
        Returns a frozenset with the columns the user does not have
        the requested level of access to

        :param request:     request object
        :param level:       access level
        :return:            frozenset of column names
        """
        perms = self.column_permissions(request, model, level)
        ret = frozenset(k for k, v in perms.items() if not v)
        return ret

    def check_model_permission(self, request, model, level):
        """
        Checks whether the user has the requested level of access to
        the model, raising PermissionDenied if not

        :param request:     request object
        :param level:       access level
        :raise:             PermissionDenied
        """
        backend = request.cache.auth_backend
        if not backend.has_permission(request, model.name, level):
            raise PermissionDenied
