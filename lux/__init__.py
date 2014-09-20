'''python web toolkit'''
VERSION = (0, 1, 0, 'alpha', 1)

import os
from pulsar.utils.version import get_version

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

__version__ = version = get_version(VERSION)
__author__ = 'Luca Sbardella'
__contact__ = "luca@quantmind.com"

from .core import *
