from lux.core import LuxCommand, Setting
from lux.utils.crypt import generate_secret


class Command(LuxCommand):
    help = "Generate a secret key."
    option_list = (
        Setting('length', ('--length',),
                default=64, type=int,
                desc=('Secret key length')),
        Setting('hex', ('--hex',),
                default=False,
                action='store_true',
                desc=('Hexadecimal string')),
    )

    def run(self, options, **params):
        return generate_secret(options.length, hexadecimal=options.hex)
