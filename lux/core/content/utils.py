from itertools import chain

from pulsar.utils.structures import mapping_iterator


def identity(x, cfg):
    return x


def guess(value):
    return value if len(value) > 1 else value[-1]


def chain_meta(meta1, meta2):
    return chain(mapping_iterator(meta1), mapping_iterator(meta2))
