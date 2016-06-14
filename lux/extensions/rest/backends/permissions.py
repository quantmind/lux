from lux.core.auth import ACTIONS
from lux.core import cached

from ..policy import has_permission


class PemissionsMixin:
    """Implements the ``has_permission`` backend action
    """
    @cached(user=True)
    def get_permission_policies(self, request):
        """Returns a list of permission policy documents for the
        current request
        """
        user = request.cache.user
        users = request.app.models.get('users')
        groups = request.app.models.get('groups')
        perms = []
        if not users or not groups or not user.is_authenticated():
            return perms
        with users.session(request) as session:
            session.add(user)
            for group in set(user.groups):
                for permission in group.permissions:
                    policy = permission.policy
                    if not isinstance(policy, list):
                        policy = (policy,)
                    perms.extend(policy)
        return perms

    def has_permission(self, request, resource, level):
        user = request.cache.user
        # Superuser, always true
        if user.is_superuser():
            return True
        else:
            # Get permissions list for the current request
            policies = self.get_permission_policies(request)
            return has_permission(request, policies, resource, level)

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
