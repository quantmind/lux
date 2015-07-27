from lux.forms import ValidationError

from .user import PERMISSION_LEVELS

POLICY = dict(effect=(str, frozenset(('allow', 'deny'))),
              action=((str, list), None),
              resource=((str, list), None),
              condition=(dict, None))

EFFECTS = {'allow': True,
           'deny': False}


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

    if 'action' not in p:
        raise ValidationError('"action" must be defined')

    return p


def _check_policies(policies, name, level):
    if isinstance(policies, dict):
        for policy in policies.values():
            permission = _has_permission(policy, name, level)
            if permission is not None:
                return permission
    return None


def _check_default_level(default, level):
    if isinstance(default, str):
        default = PERMISSION_LEVELS.get(default.upper(), 0)
    return level <= default


def has_permission(request, permissions, name, level):
    action = name
    while action:
        permission = _check_policies(permissions, action, level)
        if permission is not None:
            return permission
        else:
            default = request.config['DEFAULT_PERMISSION_LEVELS'].get(action)
            if default is not None:
                return _check_default_level(default, level)
        action = action.rpartition(':')[0]

    default = request.config['DEFAULT_PERMISSION_LEVEL']
    return _check_default_level(default, level)


def _has_permission(policy, name, level):
    actions = policy['action']
    if not isinstance(actions, list):
        actions = (actions,)
    for action in actions:
        if name == action:
            return EFFECTS[policy.get('effect', 'allow')]
    return None
