"""Multi application plugin infrastructure.

A plugin add functionalities and endpoints to an application.
"""
from collections import OrderedDict

from lux.core import app_attribute
from lux.utils.data import as_tuple


def has_plugin(app, plugin, config=None):
    cfg = app.config
    config = config or cfg
    if config['APPLICATION_ID'] == cfg['MASTER_APPLICATION_ID']:
        # The master application has all plugins
        return True
    if plugin.permission:
        return True
    return False


@app_attribute
def plugins(app):
    return Plugins(app)


class Plugins:
    """Plugin Container
    """
    def __init__(self, app):
        self.app = app
        self.plugins = OrderedDict()

    def __iter__(self):
        return iter(self.plugins.values())

    def __len__(self):
        return len(self.plugins)

    def register(self, name, plugin):
        plugin.name = name
        self.plugins[name] = plugin


class Plugin:
    """Base class for Multi-application plugin
    """
    name = None

    def __init__(self, backend=None, require=None, extensions=None,
                 permission=None):
        self.backends = as_tuple(backend)
        self.require = require
        self.extensions = as_tuple(extensions)
        self.permission = permission

    def on_config(self, config):
        for extension in self.extensions:
            if extension not in config['EXTENSIONS']:
                config['EXTENSIONS'].append(extension)
        for backend in self.backends:
            if backend not in config['AUTHENTICATION_BACKENDS']:
                config['AUTHENTICATION_BACKENDS'].append(backend)
