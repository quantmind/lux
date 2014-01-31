from pulsar import Setting

from . import startproject


class Command(startproject.Command):
    option_list = (Setting('name',
                           nargs=1,
                           desc='Extension name.'),
                   Setting('target', ['--target'],
                            desc='directory containing the extension.'))
    help = ('Creates a Lux project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')

    template_type = "extension"
