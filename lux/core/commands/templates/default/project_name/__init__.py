from pulsar.utils.version import get_version

import lux

VERSION = (0, 1, 1, 'alpha', 0)

__version__ = get_version(VERSION)


class Extension(lux.Extension):
    """${project_name}
    """
    version = __version__

    def middleware(self, app):
        return []
