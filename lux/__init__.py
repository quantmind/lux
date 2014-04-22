'''Asynchronous web framework for python'''
import os
import json

release = 'beta'


PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_pkg(name, dir=None):
    p = os.path
    dir = dir or PACKAGE_DIR
    with open(os.path.join(dir, name)) as f:
        data = f.read()
    return json.loads(data)

package = load_pkg('package.json')
media_libraries = load_pkg('libs.json')
javascript_dependencies = load_pkg('deps.json')


from .utils import version_tuple

__version__ = package['version']
VERSION = version_tuple(__version__)

from .media import *
from .commands import *
from .core import *
from .stores import *
