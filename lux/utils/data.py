from itertools import chain, zip_longest


def update_dict(source, target):
    result = source.copy()
    result.update(target)
    return result


def grouper(n, iterable, padvalue=None):
    '''grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'),
    ('g','x','x')'''
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)


def unique_tuple(*iterables):
    vals = []
    for v in chain(*[it for it in iterables if it]):
        if v not in vals:
            vals.append(v)
    return tuple(vals)


def json_dict(value):
    cfg = {}
    for key, val in value.items():
        cfg[key] = json_value(val)
    return cfg


def json_value(value):
    if isinstance(value, (int, float, str)):
        return value
    elif isinstance(value, dict):
        return json_dict(value)
    elif isinstance(value, (tuple, list, set)):
        return json_sequence(value)
    else:
        return str(value)


def json_sequence(value):
    return [json_value(v) for v in value]


def multi_pop(key, *dicts):
    value = None
    for d in dicts:
        if key in d:
            value = d.pop(key)
    return value


def as_tuple(value=None):
    if value is None:
        return ()
    elif isinstance(value, tuple):
        return value
    elif isinstance(value, (list, tuple, set, frozenset)):
        return tuple(value)
    else:
        return value,


def boolean_from_url_query(value):
    return value.lower() in ('', 'true', 'yes')
