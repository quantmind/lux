import os
import re
from os import path
from importlib import import_module
from string import Template

from pulsar import Setting
from pulsar.utils.security import random_string

import lux


def validate_name(name, app_or_project):
    # If it's not a valid directory name.
    if not re.search(r'^[_a-zA-Z]\w*$', name):
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise lux.CommandError("%r is not a valid %s name. Please %s." %
                               (name, app_or_project, message))


class Command(lux.Command):
    option_list = (Setting('luxname',
                           nargs=1,
                           desc='Name of the project.'),
                   Setting('target', ['--target'],
                           desc='directory containing the project.'))
    help = ('Creates a Lux project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')

    template_type = "project"

    def run(self, options, name=None, target=None):
        name = options.luxname[0]
        validate_name(name, self.template_type)
        # Check that the name cannot be imported.
        try:
            import_module(name)
        except ImportError:
            pass
        else:
            raise lux.CommandError("%r conflicts with the name of an existing "
                                   "Python module and cannot be used as a "
                                   "%s name.\nPlease try another name." %
                                   (name, self.template_type))
        #
        # if some directory is given, make sure it's nicely expanded
        if target is None:
            top_dir = path.join(os.getcwd(), name)
            try:
                os.makedirs(top_dir)
            except OSError as e:
                raise lux.CommandError(str(e))
        else:
            top_dir = path.abspath(path.expanduser(target))
            if not path.exists(top_dir):
                raise lux.CommandError(
                    "Destination directory '%s' does not "
                    "exist, please create it first." % top_dir)
        self.build(name, top_dir)
        self.write('%s "%s" created' % (self.template_type, name))

    def add_context(self, context):
        # Create a random SECRET_KEY hash to put it in the main settings.
        chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
        context['secret_key'] = random_string(chars, 50)

    def build(self, name, top_dir):
        base_name = '%s_name' % self.template_type
        template_dir = path.join(path.dirname(__file__),
                                 'templates', self.template_type)
        context = {base_name: name}
        self.add_context(context)
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)

            if relative_dir:
                target_dir = path.join(top_dir, relative_dir)
                if not path.exists(target_dir):
                    os.mkdir(target_dir)

            for dirname in dirs[:]:
                if dirname.startswith('.') or dirname == '__pycache__':
                    dirs.remove(dirname)

            for filename in files:
                if filename.endswith(('.pyo', '.pyc', '.py.class')):
                    continue

                old_path = path.join(root, filename)

                with open(old_path, 'r') as template_file:
                    content = template_file.read()

                content = Template(content).substitute(context)

                new_path = path.join(top_dir, relative_dir,
                                     filename.replace(base_name, name))

                with open(new_path, 'w') as new_file:
                    new_file.write(content)
