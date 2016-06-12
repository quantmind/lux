from pulsar.apps.wsgi import route

from .commands import ConsoleParser, CommandError, LuxCommand, Setting
from .extension import LuxExtension, Parameter, app_attribute
from .models import LuxModel, Query, ModelInstance
from .app import (App, Application, execute_from_config,
                  execute_app, extend_config)
from .wrappers import (WsgiRequest, Router, HtmlRouter,
                       JsonRouter, json_message, cached_property,
                       RedirectRouter, LuxContext,
                       JSON_CONTENT_TYPES, DEFAULT_CONTENT_TYPES)
from .templates import register_template_engine, template_engine, Template
from .cms import CMS
from .mail import EmailBackend
from .cache import cached, Cache, register_cache, create_cache
from .exceptions import raise_http_error, ShellError
from .auth import AuthBase, backend_action, auth_backend_actions


GET_HEAD = frozenset(('GET', 'HEAD'))
POST_PUT = frozenset(('POST', 'PUT'))


__all__ = ['ConsoleParser',
           'CommandError',
           'LuxCommand',
           'Setting',
           'LuxExtension',
           'Parameter',
           'app_attribute',
           #
           'LuxModel',
           'Query',
           'ModelInstance',
           #
           'App',
           'Application',
           'execute_from_config',
           'execute_app',
           'extend_config',
           'register_template_engine',
           'template_engine',
           'Template',
           'CMS',
           'EmailBackend',
           'cached',
           'Cache',
           'register_cache',
           'create_cache',
           'raise_http_error',
           'ShellError',
           #
           'AuthBase',
           'backend_action',
           'auth_backend_actions',
           #
           'Html',
           'WsgiRequest',
           'Router',
           'HtmlRouter',
           'JsonRouter',
           'route',
           'json_message',
           'cached_property',
           'RedirectRouter',
           'LuxContext',
           'JSON_CONTENT_TYPES',
           'DEFAULT_CONTENT_TYPES',
           'GET_HEAD',
           'POST_PUT']
