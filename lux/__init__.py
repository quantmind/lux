'''Asynchronous web framework for python'''
import os
import json
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

__version__ = '0.1a2'


def load_pkg(name, dir=None):
    p = os.path
    dir = dir or PACKAGE_DIR
    with open(os.path.join(dir, name)) as f:
        data = f.read()
    return json.loads(data)

media_libraries = load_pkg('libs.json')
javascript_dependencies = load_pkg('deps.json')

from .media import *
from .commands import *
from .core import *
from .stores import *
from pulsar import coroutine_return, async
