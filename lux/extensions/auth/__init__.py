'''
Bettery included Authentication models and Backends.
This extension requires :mod:`lux.extensions.odm` module.

It provides models for User, Groups and Permissions.
If you need something different you can use this extension as a guide on
how to write authentication backends and models in lux.
'''
import lux

from lux import Parameter
from lux.extensions import rest

from .backends import (TokenBackend, SessionBackend, BrowserBackend,
                       ApiSessionBackend)
from .views import Authorization


__all__ = ['TokenBackend', 'SessionBackend',
           'BrowserBackend', 'ApiSessionBackend',
           'Authorization']


class Extension(lux.Extension):
    _config = [
        Parameter('ANONYMOUS_GROUP', 'anonymous',
                  'Name of the group for all anonymous users'),
        Parameter('DEFAULT_PERMISSION_LEVEL', rest.READ,
                  'Default permission level')
    ]

    def on_config(self, app):
        app.require('lux.extensions.odm')

    def on_token(self, app, request, token, user):
        if user.is_authenticated():
            token['username'] = user.username
            token['user_id'] = user.id
            token['name'] = user.full_name
