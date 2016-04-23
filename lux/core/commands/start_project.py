import os
import re
from os import path
from importlib import import_module

from lux.core import LuxCommand, Setting, CommandError
from lux.utils.files import skipfile

from .generate_secret_key import generate_secret


template_dir = os.path.join(path.dirname(__file__), 'project_template')


def validate_name(name):
    # If it's not a valid directory name.
    if not re.search(r'^[_a-zA-Z]\w*$', name):
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise CommandError("%r is not a valid project name. Please %s." %
                           (name, message))


class Command(LuxCommand):
    option_list = (
        Setting('luxname',
                nargs='?',
                desc='Name of the project.'),
    )
    help = ('Creates a Lux project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')

    def run(self, options):
        if not options.luxname:
            raise CommandError("A project name is required")
        name = options.luxname
        validate_name(name)
        target = path.join(os.getcwd(), '%s-project' % name)

        if path.exists(target):
            raise CommandError("%r conflicts with an existing path" % target)

        # Check that the name cannot be imported.
        try:
            import_module(name)
        except ImportError:
            pass
        else:
            raise CommandError("%r conflicts with the name of an "
                               "existing Python module and cannot be "
                               "used as a name.\n"
                               "Please try another name." % name)
        #
        # if some directory is given, make sure it's nicely expanded
        try:
            os.makedirs(target)
        except OSError as e:
            raise CommandError(str(e)) from e

        self.build(name, target)
        self.write('Project "%s" created' % name)
        return target

    def build(self, name, target):
        render = self.app.template_engine()
        base_name = 'project_name'
        context = {base_name: name,
                   'secret_key': generate_secret(50)}
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)

            if relative_dir:
                target_dir = path.join(target, relative_dir)
                if not path.exists(target_dir):
                    os.mkdir(target_dir)

            for dirname in dirs[:]:
                if skipfile(dirname):
                    dirs.remove(dirname)

            for filename in files:
                if (skipfile(filename) or
                        filename.endswith(('.pyo', '.pyc', '.py.class'))):
                    continue

                old_path = path.join(root, filename)

                with open(old_path, 'r') as template_file:
                    content = template_file.read()

                if not filename.endswith('.html'):
                    content = render(content, context)

                new_path = path.join(target, relative_dir,
                                     filename.replace(base_name, name))

                with open(new_path, 'w') as new_file:
                    new_file.write(content)
