"""Asynchronous web framework for python
"""
import os

VERSION = (0, 7, 0, 'alpha', 0)
__author__ = 'Luca Sbardella'
__contact__ = "luca@quantmind.com"
__homepage__ = "https://github.com/quantmind/lux"
__license__ = "BSD"
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


if os.environ.get('lux_install_running') != 'yes':
    from pulsar.utils.version import get_version

    __version__ = version = get_version(VERSION, __file__)

    from .core import *     # noqa
