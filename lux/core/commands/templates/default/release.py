import os
import json
from importlib import import_module

from pulsar.apps.release import ReleaseManager
version_file = os.path.join(os.path.dirname(__file__),
                            '$project_name', '__init__.py')


def before_commit(manager, release):
    """Update the package.json version
    """
    mod = import_module('$project_name')

    manager.logger.info('Update package.json')

    for filename in ('package.json', 'bower.json'):
        with open(filename, 'r') as f:
            pkg = json.loads(f.read())

        pkg['version'] = mod.__version__
        pkg['description'] = mod.__doc__

        with open(filename, 'w') as f:
            f.write(json.dumps(pkg, indent=4))


if __name__ == '__main__':
    ReleaseManager(config='release.py').start()
