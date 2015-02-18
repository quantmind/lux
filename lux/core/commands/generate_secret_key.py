from random import randint

from pulsar import Setting
from pulsar.utils.security import random_string

import lux


def generate_secret(length, hexadecimal=False):
    if hexadecimal:
        return ''.join((hex(randint(1, 10000)) for _ in range(length)))
    else:
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        return random_string(chars, length)


class Command(lux.Command):
    help = "Show parameters."
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
        self.write('Secret key:')
        self.write(generate_secret(options.length, options.hex))
        self.write('-----------------------------------------------------')
