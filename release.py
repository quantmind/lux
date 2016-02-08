import json

from agile import AgileManager

app_module = 'lux'
note_file = 'docs/notes.md'
docs_bucket = 'quantmind-docs'


def before_commit(manager, release):
    """Update the package.json version
    """
    import lux

    manager.logger.info('Update package.json')

    with open('example/package.json', 'r') as f:
        pkg = json.loads(f.read())

    pkg['version'] = lux.__version__
    pkg['description'] = lux.__doc__

    with open('example/package.json', 'w') as f:
        f.write(json.dumps(pkg, indent=4))


if __name__ == '__main__':
    AgileManager(config='release.py').start()
