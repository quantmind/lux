from lux.core import LuxCommand
from lux.utils.crypt import create_uuid


class Command(LuxCommand):
    help = "Create a Universal Unique Identifier"

    def run(self, options, **params):
        result = create_uuid().hex
        self.write(result)
        return result
