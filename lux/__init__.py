"""Asynchronous web framework for python"""
import os

from .utils.version import get_version

VERSION = (0, 7, 0, 'alpha', 0)

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
__version__ = version = get_version(VERSION, __file__)
