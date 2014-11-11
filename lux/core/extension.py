import os
import sys
import logging
from copy import copy
from inspect import getfile

from pulsar.utils.path import Path
from pulsar.utils.pep import native_str

from lux import __version__


__all__ = ['Extension', 'Parameter']


class Parameter(object):
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
    def __init__(self, name, default, doc):
        self.name = name
        self.default = default
        self.doc = doc
        self.extension = None

    def __repr__(self):
        return '%s: %s' % (self.name, self.default)
    __str__ = __repr__


class ExtensionMeta(object):
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

    def __init__(self, file, version, config=None):
        file = Path(file)
        if file.isdir():
            appdir = file
        else:
            appdir = file.realpath().parent
        self.file = file
        self.path = appdir.realpath()
        self.version = version or __version__
        if self.has_module:
            _, name = self.path.split()
        else:
            # otherwise it is the name of the file
            _, name = self.file.split()
        self.name = name
        self.config = cfg = {}
        if config:
            for setting in config:
                setting = copy(setting)
                setting.extension = self.name
                cfg[setting.name] = setting

    def __repr__(self):
        return self.name

    def add_to_pypath(self):
        if self.has_module:
            base, _ = self.path.split()
            if base not in sys.path:
                sys.path.append(str(base))

    @property
    def has_module(self):
        return True
        return self.path.ispymodule()

    @property
    def media_dir(self):
        '''Directory containing media files (if available)'''
        if self.has_module:
            dir = os.path.join(self.path, 'media')
            if os.path.isdir(dir):
                return dir

    def copy(self, file):
        meta = self.__class__(file, self.version, self.config.values())
        meta.script = self.script
        meta.argv = copy(self.argv)
        return meta

    def update_config(self, config):
        for setting in config.values():
            self.config[setting.name] = copy(setting)


class ExtensionType(type):
    '''Little magic to setup the extension'''
    def __new__(cls, name, bases, attrs):
        config = attrs.pop('_config', None)
        version = attrs.pop('version', None)
        abstract = attrs.pop('abstract', False)
        klass = super(ExtensionType, cls).__new__(cls, name, bases, attrs)
        if not abstract:
            meta = getattr(klass, 'meta', None)
            if isinstance(meta, ExtensionMeta):
                cfg = list(meta.config.values())
                if config:
                    cfg.extend(config)
                meta = ExtensionMeta(getfile(klass), version, cfg)
            else:
                meta = ExtensionMeta(getfile(klass), version, config)
            klass.meta = meta
        return klass


class Extension(ExtensionType('ExtBase', (object,), {'abstract': True})):
    '''Base class for extensions including the :class:`.Application` class.

    .. attribute:: meta

        The :class:`ExtensionMeta` data created by the :class:`Extension`
        metaclass.

    .. attribute:: logger

        The logger instance for this :class:`Extension`.
    '''
    abstract = True

    def middleware(self, app):
        '''Called by application ``app`` when creating the middleware.

        This method is invoked the first time :attr:`.App.handler` attribute
        is accessed. It must return a list of WSGI middleware or ``None``.
        '''
        pass

    def response_middleware(self, app):
        '''Called by application ``app`` when creating the response
        middleware'''
        pass

    def setup_logger(self, config, opts):
        '''Called by :meth:`setup` method to setup the :attr:`logger`.'''
        self.logger = logging.getLogger('lux.%s' % self.meta.name)

    def setup(self, module, params, opts=None):
        '''Internal method which prepare the extension for usage.
        '''
        config = {}
        for setting in self.meta.config.values():
            if setting.name in params:
                value = params[setting.name]
            else:
                value = getattr(module, setting.name, setting.default)
            config[setting.name] = value
        self.setup_logger(config, opts)
        return config

    def extra_form_data(self, request):
        '''Must return an iterable over key-value pair of data to add to a
        :class:`.Form`.

        By default it returns an empty tuple.
        '''
        return ()

    def write(self, msg='', stream=None):
        '''Write ``msg`` into ``stream`` or ``sys.stdout``
        '''
        h = stream or sys.stdout
        if msg:
            h.write(native_str(msg))
        h.write('\n')

    def write_err(self, msg='', stream=None):
        '''Write ``msg`` into ``stream`` or ``sys.stderr``
        '''
        h = stream or sys.stderr
        if msg:
            h.write(native_str(msg))
        h.write('\n')

    def check(self, request, data):
        pass

    def __repr__(self):
        return self.meta.__repr__()

    def __str__(self):
        return self.__repr__()


class EventHandler:
    __slots__ = ('extension', 'name')

    def __init__(self, extension, name):
        self.extension = extension
        self.name = name

    def __repr__(self):
        return '%s.%s' % (self.extension, self.name)
    __str__ = __repr__

    def __call__(self, *args):
        return getattr(self.extension, self.name)(*args)
