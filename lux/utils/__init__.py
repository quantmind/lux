import string
from itertools import chain
from random import choice
from collections import Hashable
from functools import partial

from pulsar.utils.httpurl import *
from pulsar.utils.pep import range, ispy3k, to_string
from pulsar.utils.version import get_version

if ispy3k:  # pragma nocover
    characters = string.ascii_letters + string.digits
else:   # pragma nocover
    characters = string.letters + string.digits


def unique_tuple(*iterables):
    vals = []
    for v in chain(*[it for it in iterables if it]):
        if v not in vals:
            vals.append(v)
    return tuple(vals)


def random_string(characters=None, len=20):
    characters or default_characters
    return ''.join((choice(characters) for s in range(len)))


class memoized(object):
    """Function decorator to cache return values.

    If called later with the same arguments, the cached value is returned
    (not reevaluated).

    """
    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return partial(self.__call__, obj)
