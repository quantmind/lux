"""Asynchronous web framework for python"""
import os

from .utils.version import get_version

VERSION = (0, 9, 0, 'alpha', 1)

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
__version__ = version = get_version(VERSION, __file__)
