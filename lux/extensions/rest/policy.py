from lux.forms import ValidationError


POLICY = dict(effect=(str, frozenset(('allow', 'deny'))),
              # An action is a string or a list of PERMISSION_LEVELS
              action=((str, list), None),
              # A resource can be a string or a list of resources.
              # A resource is object/model we are checking permission
              resource=((str, list), None),
              # Additional condition (not yet used)
              condition=(dict, None))

EFFECTS = {'allow': True,
           'deny': False}


def has_permission(request, permissions, resource, action):
    '''Check for permission to perform an ``action`` on a ``resource``
    '''
    while resource:
        permission = _check_policies(permissions, resource, action)
        if permission is not None:
            return permission
        else:
            default = request.config['DEFAULT_PERMISSION_LEVELS'].get(resource)
            if default is not None:
                return _has_policy_actions(action, default)
        resource = resource.rpartition(':')[0]

    default = request.config['DEFAULT_PERMISSION_LEVEL']
    return _has_policy_actions(action, default)


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


def _check_policies(policies, resource, action):
    """
    Checks an action against a list of policies
    :param policies:    dict of policies
    :param name:        action name
    :param level:       access level
    :return:            True if access is granted, False if denied,
                        None if no specific determination made
    """
    if isinstance(policies, dict):
        for policy in policies.values():
            permission = _has_permission(policy, resource, action)
            if permission is not None:
                return permission
    return None


def _has_policy_actions(action, actions):
    if actions == '*':
        return True
    elif isinstance(actions, (list, tuple)):
        for act in actions:
            if _has_policy_actions(action, act):
                return True
    elif isinstance(action, str) and isinstance(actions, str):
        return action.lower() == actions.lower()


def _has_permission(policy, resource, action):
    resources = policy.get('resource')
    if resources:
        if not isinstance(resources, list):
            resources = (resources,)
        for available_resource in resources:
            if available_resource == resource:
                if _has_policy_actions(action, policy.get('action')):
                    return EFFECTS.get(policy.get('effect', 'allow'))
    return None
