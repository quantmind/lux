"""Battery included Authentication models and Backends.
This extension requires the :mod:`lux.extensions.rest` module.

It provides models for Users, Groups and Permissions.
If you need something different you can use this extension as a guide on
how to write authentication backends and models in lux.
"""
from pulsar.utils.slugify import slugify

from lux.core import Parameter, LuxExtension
from lux.forms import ValidationError

# make sure to import forms
from . import forms     # noqa
from .backends import TokenBackend
from .rest.authorization import Authorization
from .rest.groups import GroupCRUD
from .rest.mailinglist import MailingListCRUD
from .rest.passwords import PasswordsCRUD
from .rest.permissions import PermissionCRUD
from .rest.registrations import RegistrationCRUD
from .rest.tokens import TokenCRUD
from .rest.user import UserRest, UserModel
from .rest.users import UserCRUD


__all__ = [
    'TokenBackend',
    'Authorization',
    'GroupCRUD',
    'MailingListCRUD',
    'PasswordsCRUD',
    'PermissionCRUD',
    'RegistrationCRUD',
    'TokenCRUD',
    'UserCRUD',
    'UserRest',
    'UserModel'
]


class Extension(LuxExtension):
    _config = [
        Parameter('GENERAL_MAILING_LIST_TOPIC', 'general',
                  "topic for general mailing list"),
        Parameter('ACCOUNT_ACTIVATION_DAYS', 2,
                  'Number of days the activation code is valid'),
        Parameter('CRYPT_ALGORITHM',
                  'lux.utils.crypt.pbkdf2',
                  'Python dotted path to module which provides the '
                  '``encrypt`` and, optionally, ``decrypt`` method for '
                  'password and sensitive data encryption/decryption'),
        Parameter('PASSWORD_SECRET_KEY',
                  None,
                  'A string or bytes used for encrypting data. Must be unique '
                  'to the application and long and random enough'),
        Parameter('CHECK_USERNAME', 'lux.extensions.auth:check_username',
                  'Dotted path to username validation function')
    ]

    def on_config(self, app):
        self.require(app, 'lux.extensions.odm')
        if not app.config['PASSWORD_SECRET_KEY']:
            app.config['PASSWORD_SECRET_KEY'] = app.config['SECRET_KEY']

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
                PasswordsCRUD(),
                MailingListCRUD(),
                TokenCRUD())


def check_username(request, username):
    """Default function for checking username validity
    """
    correct = slugify(username)
    if correct != username:
        raise ValidationError('Username may only contain lowercase '
                              'alphanumeric characters or single hyphens, '
                              'cannot begin or end with a hyphen')
    elif len(correct) < 2:
        raise ValidationError('Too short')
    return username
