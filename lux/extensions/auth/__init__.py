'''
Bettery included Authentication models and Backends.
This extension requires :mod:`lux.extensions.odm` module.

It provides models for User, Groups and Permissions.
If you need something different you can use this extension as a guide on
how to write authentication backends and models in lux.
'''
import lux

from .backends import TokenBackend, SessionBackend


__all__ = ['TokenBackend', 'SessionBackend']


class Extension(lux.Extension):

    def on_token(self, app, request, token, user):
        if user.is_authenticated():
            token['username'] = user.username
            token['user_id'] = user.id
            token['name'] = user.full_name()
