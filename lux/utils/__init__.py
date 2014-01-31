import string
from itertools import chain
from random import choice

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
