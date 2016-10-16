from itertools import chain

from lux.core.auth import ACTIONS
from lux.core import cached
from lux.forms import ValidationError


POLICY = dict(effect=(str, frozenset(('allow', 'deny'))),
              # An action is a string, a wildcard or a list of actions
              action=((str, list), None),
              # A resource can be a string or a list of resources.
              # A resource is object/model we are checking permission
              resource=((str, list), None),
              # Additional condition to evaluate
              condition=(str, None))

EFFECTS = {'allow': True,
           'deny': False}


class PemissionsMixin:
    """Implements the ``has_permission`` and ``get_permissions``
    auth backend actions
    """
    def has_permission(self, request, resource, action):
        user = request.cache.user
        # Superuser, always true
        if user.is_superuser():
            return True
        else:
            # Get permissions list for the current request
            policies = self.get_permission_policies(request)
            return has_permission(request, policies, resource, action)

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

    @cached(user=True)
    def get_permission_policies(self, request):
        """Returns a list of permission policy documents for the
        current request

        Cache results on a user basis
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


def user_permissions(request):
    """Return a dictionary of permissions for the current user

    :request: a WSGI request with url data ``resource`` and ``action``.
    """
    backend = request.cache.auth_backend
    resources = request.url_data.get('resource', ())
    actions = request.url_data.get('action')
    return backend.get_permissions(request, resources, actions=actions)


def has_permission(request, policies, resource, action):
    '''Check for permission to perform an ``action`` on a ``resource``

    :param permissions: dictionary or permissions
    :param resource: resource string, colon separated
    :param action: action to check permission for
    '''
    namespaces = resource.split(':')
    available_policies = []
    #
    # First select appropriate policies
    for policy in chain(policies, request.config['DEFAULT_POLICY']):
        resources = policy.get('resource')
        if resources and _has_policy_actions(action, policy.get('action')):
            effect = EFFECTS.get(policy.get('effect', 'allow'))
            condition = policy.get('condition')
            if not isinstance(resources, list):
                resources = (resources,)
            for available_resource in resources:
                bits = available_resource.split(':')
                if len(bits) > len(namespaces):
                    continue
                available_policies.append((bits, effect, condition))

    if not available_policies:
        return False

    context = {
        'user': request.cache.user,
        'env': request.cache
    }

    while namespaces:
        has = {}
        for policy, effect, condition in available_policies:
            if len(policy) != len(namespaces):
                continue

            match = {}
            count = 0
            for a, b in zip(namespaces, policy):
                if a == b:
                    continue
                elif b == '*':
                    match[count] = a
                    count += 1
                else:
                    match = False
                    break

            if match is False:  # No match
                continue

            if condition:
                local = {'match': match}
                try:
                    if not eval(condition, context, local):
                        continue
                except Exception as exc:
                    request.logger.error(
                        'Could not evaluate policy condition "%s" '
                        'on resource "%s": %s',
                        condition, resource, exc)
                    return False

            if not match and not effect:
                return False

            if has.get(len(match)) is not False:
                has[len(match)] = effect

        if has:
            return has[sorted(has)[0]]

        namespaces.pop()

    return False


def validate_policy(policy):
    if isinstance(policy, dict):
        return validate_single_policy(policy)
    elif isinstance(policy, list):
        if not policy:
            raise ValidationError('Policy empty')
        policies = []
        for single in policy:
            policies.append(validate_single_policy(single))
        return policies
    else:
        raise ValidationError('Policy should be a list or an object')


def validate_single_policy(policy):
    if not isinstance(policy, dict):
        raise ValidationError('Policy should be a list or an object')

    p = {}
    for key, value in policy.items():
        key = str(key).lower()
        if key not in POLICY:
            statements = ', '.join(POLICY)
            raise ValidationError('"%s" is not a valid statement. '
                                  'Must be one of %s' % (key, statements))
        types, check = POLICY[key]
        if not isinstance(value, types):
            raise ValidationError('not a valid %s statement' % key)
        if check:
            if isinstance(value, str):
                value = value.lower()
            if value not in check:
                raise ValidationError('not a valid %s statement' % key)
        p[key] = value

    if 'resource' not in p:
        raise ValidationError('"resource" must be defined')

    if 'action' not in p:
        raise ValidationError('"action" must be defined')

    return p


def _has_policy_actions(action, actions):
    if actions == '*':
        return True
    elif isinstance(actions, (list, tuple)):
        for act in actions:
            if _has_policy_actions(action, act):
                return True
    elif isinstance(action, str) and isinstance(actions, str):
        return action.lower() == actions.lower()
