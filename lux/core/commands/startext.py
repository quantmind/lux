from . import startproject


class Command(startproject.Command):
    help = ('Creates a Lux application directory structure for the given '
            'application name in the current directory')

    template_type = "extension"

    def add_context(self, context):
        pass
