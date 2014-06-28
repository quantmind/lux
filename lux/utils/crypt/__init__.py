from os import urandom
import string
import random
from hashlib import sha1

from pulsar.utils.pep import ispy3k


if ispy3k:
    default_choices = string.digits + string.ascii_letters
else:   # pragma    nocover
    default_choices = string.digits + string.letters
    range = xrange


def get_random_string(length, allowed_chars=None):
    allowed_chars = allowed_chars or default_choices
    return ''.join([random.choice(allowed_chars) for i in range(length)])


def generate_secret_key(length=64, allowed_chars=None):
    allowed_chars = allowed_chars or default_choices + string.punctuation
    return get_random_string(length, allowed_chars)


def digest(value, salt_size=8):
    salt = urandom(salt_size)
    return sha1(salt+value.encode('utf-8')).hexdigest()
