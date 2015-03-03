import os
import re
from os import path
from importlib import import_module
from string import Template

from pulsar import Setting

import lux

from .generate_secret_key import generate_secret


def validate_name(name):
    # If it's not a valid directory name.
    if not re.search(r'^[_a-zA-Z]\w*$', name):
        # Provide a smart error message, depending on the error.
        if not re.search(r'^[_a-zA-Z]', name):
            message = 'make sure the name begins with a letter or underscore'
        else:
            message = 'use only numbers, letters and underscores'
        raise lux.CommandError("%r is not a valid project name. Please %s." %
                               (name, message))


class Command(lux.Command):
    option_list = (Setting('luxname',
                           nargs='?',
                           desc='Name of the project.'),
                   Setting('template', ('--template',),
                           default='default',
                           desc='Site template'),
                   Setting('template_list', ('--template-list',),
                           default=False,
                           action='store_true',
                           desc='List of available site templates')
                   )
    help = ('Creates a Lux project directory structure for the given '
            'project name in the current directory or optionally in the '
            'given directory.')

    def run(self, options):
        self.template_dir = path.join(path.dirname(__file__), 'templates')
        if options.template_list:
            for name in os.listdir(self.template_dir):
                dir = os.path.join(self.template_dir, name)
                if os.path.isdir(dir) and not name.startswith('_'):
                    self.write(name)
        else:
            template = options.template
            template_dir = path.join(self.template_dir, template)
            if not os.path.isdir(template_dir):
                raise lux.CommandError('Unknown template project "%s"'
                                       % template)
            if not options.luxname:
                raise lux.CommandError("A project name is required")
            name = options.luxname
            validate_name(name)
            self.target = path.join(os.getcwd(), '%s-project' % name)
            if path.exists(self.target):
                raise lux.CommandError("%r conflicts with an existing path"
                                       % self.target)

            # Check that the name cannot be imported.
            try:
                import_module(name)
            except ImportError:
                pass
            else:
                raise lux.CommandError("%r conflicts with the name of an "
                                       "existing Python module and cannot be "
                                       "used as a %s name.\n"
                                       "Please try another name." %
                                       (name, self.template_type))
            #
            # if some directory is given, make sure it's nicely expanded
            try:
                os.makedirs(self.target)
            except OSError as e:
                raise lux.CommandError(str(e))

            self.build(options.template, name)
            self.write('Project "%s" created' % name)

    def build(self, template, name):
        base_name = 'project_name'
        template_dir = path.join(self.template_dir, template)
        context = {base_name: name,
                   'secret_key': generate_secret(50)}

        if template != 'default':
            default_dir = path.join(self.template_dir, 'default')
            self._write(name, base_name, default_dir, context)
        self._write(name, base_name, template_dir, context)

    def _write(self, name, base_name, template_dir, context):
        prefix_length = len(template_dir) + 1

        for root, dirs, files in os.walk(template_dir):
            path_rest = root[prefix_length:]
            relative_dir = path_rest.replace(base_name, name)

            if relative_dir:
                target_dir = path.join(self.target, relative_dir)
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

                if not filename.endswith('.html'):
                    content = Template(content).substitute(context)

                new_path = path.join(self.target, relative_dir,
                                     filename.replace(base_name, name))

                with open(new_path, 'w') as new_file:
                    new_file.write(content)
