'''python web toolkit'''
import os

VERSION = (0, 3, 0, 'alpha', 0)
__author__ = 'Luca Sbardella'
__contact__ = "luca@quantmind.com"
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))


if os.environ.get('lux_install_running') != 'yes':
    from pulsar.utils.version import get_version

    __version__ = version = get_version(VERSION, __file__)

    from .core import *     # noqa
