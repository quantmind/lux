"""Battery included Authentication models and Backends.
This extension requires the :mod:`lux.extensions.rest` module.

It provides models for Users, Groups and Permissions.
If you need something different you can use this extension as a guide on
how to write authentication backends and models in lux.
"""
from lux.core import Parameter, LuxExtension

from .backends import TokenBackend
from .rest import (UserRest, UserCRUD, GroupCRUD, PermissionCRUD,
                   RegistrationCRUD, TokenCRUD,
                   Authorization, Passwords)
from .mail import MailingListCRUD
from .forms import UserModel


__all__ = ['TokenBackend',
           'Authorization',
           'ComingSoon',
           'UserModel']


class Extension(LuxExtension):
    _config = [
        Parameter('GENERAL_MAILING_LIST_TOPIC', 'general',
                  "topic for general mailing list"),
        Parameter('ACCOUNT_ACTIVATION_DAYS', 2,
                  'Number of days the activation code is valid')
    ]

    def on_config(self, app):
        self.require(app, 'lux.extensions.rest')

    def on_token(self, app, request, token, user):
        if user and user.is_authenticated():
            token['username'] = user.username
            token['user_id'] = user.id
            token['name'] = user.full_name

    def api_sections(self, app):
        return (Authorization(),
                UserRest(),
                UserCRUD(),
                GroupCRUD(),
                PermissionCRUD(),
                RegistrationCRUD(),
                Passwords(),
                MailingListCRUD(),
                TokenCRUD())
