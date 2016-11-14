from os import urandom
import uuid
import string
from random import randint
from hashlib import sha1

from pulsar.utils.string import random_string

digits_letters = string.digits + string.ascii_letters
secret_choices = digits_letters + ''.join(
    (p for p in string.punctuation if p != '"')
)


def generate_secret(length=64, allowed_chars=None, hexadecimal=False):
    if hexadecimal:
        return ''.join((hex(randint(1, 10000)) for _ in range(length)))
    return random_string(length, length, allowed_chars or secret_choices)


def digest(value, salt_size=8):
    salt = urandom(salt_size)
    return sha1(salt+value.encode('utf-8')).hexdigest()


def create_uuid():
    return uuid.uuid4()


def create_token():
    return create_uuid().hex


def as_hex(value):
    if isinstance(value, uuid.UUID):
        return value.hex
    return value
