from lux.core import LuxCommand


class Command(LuxCommand):
    help = "Dummy command, it returns the application object."

    def run(self, options):
        return self.app
