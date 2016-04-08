from random import randint

from pulsar.utils.string import random_string

from lux.core import LuxCommand, Setting


def generate_secret(length=50, hexadecimal=False):
    if hexadecimal:
        return ''.join((hex(randint(1, 10000)) for _ in range(length)))
    else:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return random_string(min_len=length, max_len=length,
                             char=chars)


class Command(LuxCommand):
    help = "Generate a secret key."
    option_list = (
        Setting('length', ('--length',),
                default=50, type=int,
                desc=('Secret key length')),
        Setting('hex', ('--hex',),
                default=False,
                action='store_true',
                desc=('Hexadecimal string')),
    )

    def run(self, options, **params):
        key = generate_secret(options.length, options.hex)
        self.write('Secret key:')
        self.write(key)
        self.write('-----------------------------------------------------')
        return key
