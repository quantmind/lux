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
