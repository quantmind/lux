"""Battery included Authentication models and Backends.
This extension requires the :mod:`lux.extensions.rest` module.

It provides models for Users, Groups and Permissions.
If you need something different you can use this extension as a guide on
how to write authentication backends and models in lux.
"""
from lux.core import Parameter, LuxExtension

from .backends import TokenBackend, SessionBackend
from .rest import (UserRest, UserCRUD, GroupCRUD, PermissionCRUD,
                   RegistrationCRUD, MailingListCRUD, TokenCRUD)
from .mail import Authorization, ComingSoon
from .forms import UserModel


__all__ = ['TokenBackend',
           'SessionBackend',
           'Authorization',
           'ComingSoon',
           'UserModel']


class Extension(LuxExtension):
    _config = [
        Parameter('ANONYMOUS_GROUP', 'anonymous',
                  'Name of the group for all anonymous users'),
        Parameter('GENERAL_MAILING_LIST_TOPIC', 'general',
                  "topic for general mailing list"),
        Parameter('COMING_SOON_URL', None, "server the coming-soon page")
    ]

    def on_config(self, app):
        self.require(app, 'lux.extensions.rest')

    def middleware(self, app):
        soon = app.config['COMING_SOON_URL']
        if soon:
            yield ComingSoon(soon)

    def on_token(self, app, request, token, user):
        if user and user.is_authenticated():
            token['username'] = user.username
            token['user_id'] = user.id
            token['name'] = user.full_name

    def api_sections(self, app):
        return (UserRest(),
                UserCRUD(),
                GroupCRUD(),
                PermissionCRUD(),
                RegistrationCRUD(),
                MailingListCRUD(),
                TokenCRUD())
