import os
import json

from agile.release import ReleaseManager
version_file = os.path.join(os.path.dirname(__file__), 'lux', '__init__.py')


def before_commit(manager, release):
    """Update the package.json version
    """
    import lux

    manager.logger.info('Update package.json')

    with open('package.json', 'r') as f:
        pkg = json.loads(f.read())

    pkg['version'] = lux.__version__
    pkg['description'] = lux.__doc__

    with open('package.json', 'w') as f:
        f.write(json.dumps(pkg, indent=4))


if __name__ == '__main__':
    ReleaseManager(config='release.py').start()
