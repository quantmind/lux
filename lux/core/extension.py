import os
import sys
import logging
from copy import copy
from inspect import getfile, getmodule

from pulsar.api import ImproperlyConfigured

from lux import __version__

from .routers import JsonRouter, HtmlRouter


__all__ = ['LuxExtension', 'Parameter']


# All events are fired with app as first positional argument
ALL_EVENTS = (
    'on_config',  # Config ready.
    'on_loaded',  # Wsgi handler ready.
    'on_start',  # Wsgi server starts. Extra args: server
    'on_request',  # New client request. Extra args: request
    'on_html_document',  # Html doc built. Extra args: request, html
    'on_form',      # form data, data = (request, data, files)
    'on_create',    # create new model, data = (model, data)
    'on_close',  # Close the application - cleanup
)


class Parameter:
    '''Class for defining a lux :ref:`parameter <parameters>` within
    a lux :class:`.Extension`.

    Parameters are specified in the ``_config`` list of an :class:`.Extension`.
    For example::

        from lux import Extension, Parameter

        class MyExtension(Extension):

            _config = [
                Parameter('MYPARAM', 'Hello',
                          'A parameter for my great extension')
                ]

    :parameter name: unique name identifying the parameter which is used
        to retrieve it from the :class:`.Application.config` dictionary.
    :parameter default: the default value of the parameter. This is the value
        used by the framework when the parameter is not found in the config
        file.
    :parameter doc: a documentation string for the parameter.

    Parameters are case insensitive.
    '''
    def __init__(self, name, default, doc='', jscontext=False):
        self.name = name
        self.default = default
        self.doc = doc
        self.extension = None
        self.jscontext = jscontext
        self.override = False

    def __repr__(self):
        return '%s: %s' % (self.name, self.default)
    __str__ = __repr__


class ExtensionMeta:
    '''Contains metadata for an :class:`.Extension`.

    .. attribute:: config

        Dictionary of configuration :class:`.Parameter` for the extension.

    .. attribute:: script

        Set at runtime by :func:`execute`, it is the script
        name which runs the application.

    .. attribute:: version

        Extension version number (specified via the :class:`.Extension`
        ``version`` class attribute).
    '''
    script = None
    argv = None

    def __init__(self, module, version, config=None):
        file = getfile(module)
        dir, filename = os.path.split(file)
        self.module_name = module.__name__
        name = self.module_name
        if not filename.startswith('__init__.') and dir:
            name = '.'.join(self.module_name.split('.')[:-1])
        self.file = file
        self.path = dir
        self.version = version or __version__
        self.name = name
        self.config = cfg = {}
        if config:
            for setting in config:
                setting = copy(setting)
                setting.extension = self.name
                cfg[setting.name] = setting

    def __repr__(self):
        return self.name

    @property
    def media_dir(self):
        '''Directory containing media files (if available)'''
        dir = os.path.join(self.path, 'media')
        if os.path.isdir(dir):
            return dir

    def copy(self, module):
        meta = self.__class__(module, self.version, self.config.values())
        meta.script = self.script
        meta.argv = copy(self.argv)
        return meta

    def update_config(self, config):
        for setting in config.values():
            self.config[setting.name] = copy(setting)


class ExtensionType(type):
    '''Little magic to setup the extension'''
    def __new__(cls, name, bases, attrs):
        config = []
        on_config = []
        for base in bases:
            cfg = getattr(base, '_config', None)
            if isinstance(cfg, (list, tuple)):
                config.extend(cfg)

        version = attrs.pop('version', None)
        abstract = attrs.pop('abstract', False)
        cfg = attrs.get('_config') if abstract else attrs.pop('_config', None)
        if cfg:
            config.extend(cfg)
        if on_config:
            attrs['_on_config'] = on_config
        klass = super().__new__(cls, name, bases, attrs)
        if not abstract:
            meta = getattr(klass, 'meta', None)
            module = getmodule(klass)
            if isinstance(meta, ExtensionMeta):
                cfg = list(meta.config.values())
                if config:
                    cfg.extend(config)
                meta = ExtensionMeta(module, version, cfg)
            else:
                meta = ExtensionMeta(module, version, config)
            klass.meta = meta
        return klass


class LuxExtension(metaclass=ExtensionType):
    '''Base class for extensions including the :class:`.Application` class.

    .. attribute:: meta

        The :class:`ExtensionMeta` data created by the :class:`Extension`
        metaclass.

    .. attribute:: logger

        The logger instance for this :class:`Extension`.
    '''
    abstract = True
    stdout = None
    stderr = None
    json_router = JsonRouter
    html_router = HtmlRouter

    def routes(self, app):
        '''Called by application ``app`` when creating the middleware.

        This method is invoked the first time :attr:`.App.handler` attribute
        is accessed. It must return a list of WSGI middleware or ``None``.
        '''
        pass

    def require(self, app, *extensions):
        for ext in extensions:
            if ext not in app.config['EXTENSIONS']:
                raise ImproperlyConfigured(
                    '"%s" extension requires "%s" extension' % (self, ext))

    def setup(self, config, values, prefix=None, opts=None):
        """Internal method which prepare the extension for usage.
        """
        parameters = config['_parameters']
        for setting in self.meta.config.values():
            name = setting.name
            if name in parameters:
                setting.override = True
            parameters[name] = setting
            env = '%s_%s' % (prefix, name) if prefix else name
            value = os.environ.get(env, values.get(name, setting.default))
            config[name] = value
        self._setup_logger(config, opts)

    def get_template_full_path(self, app, name):
        '''Full path for a template name
        '''
        return os.path.join(self.meta.path, 'templates', name)

    def write(self, msg=''):
        '''Write ``msg`` into :attr:`stdout` or ``sys.stdout``
        '''
        out = self.stdout or sys.stdout
        if msg:
            out.write(msg)
        out.write('\n')

    def write_err(self, msg=''):
        '''Write ``msg`` into :attr:`stderr` or ``sys.stderr``
        '''
        out = self.stderr or sys.stderr
        if msg:
            out.write(msg)
        out.write('\n')

    def check(self, request, data):
        pass

    def sorted_config(self):
        for key in sorted(self.meta.config):
            yield key, self.meta.config[key]

    def __repr__(self):
        return self.meta.__repr__()

    def __str__(self):
        return self.__repr__()

    def _setup_logger(self, config, opts):
        '''Called by :meth:`setup` method to setup the :attr:`logger`.'''
        self.logger = logging.getLogger(self.meta.name)
