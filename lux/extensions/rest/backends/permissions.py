from lux.core.auth import ACTIONS
from ..policy import has_permission


class PemissionsMixin:
    """Implements the ``has_permission`` backend action
    """
    def get_permission_policies(self, request):
        raise NotImplementedError

    def has_permission(self, request, resource, level):
        user = request.cache.user
        # Superuser, always true
        if user.is_superuser():
            return True
        else:
            # Get permissions list for the current request
            permissions = self.get_permission_policies(request)
            return has_permission(request, permissions, resource, level)

    def get_permissions(self, request, resources, actions=None):
        if not actions:
            actions = tuple(ACTIONS)
        if not isinstance(actions, (list, tuple)):
            actions = (actions,)
        if not isinstance(resources, (list, tuple)):
            resources = (resources,)

        obj = {}

        if not request.cache.user.is_superuser():
            permissions = self.get_permission_policies(request)
            for resource in resources:
                perms = {}
                for action in actions:
                    perms[action] = has_permission(request, permissions,
                                                   resource, action)
                obj[resource] = perms

        else:
            for resource in resources:
                obj[resource] = dict(((a, True) for a in actions))

        return obj
