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


from .utils import version_tuple

__version__ = package['version']
VERSION = version_tuple(__version__)

from .core import *
