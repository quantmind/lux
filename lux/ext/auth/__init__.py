"""Battery included Authentication models and Backends.
This extension requires the :mod:`lux.extensions.rest` module.

It provides models for Users, Groups and Permissions.
If you need something different you can use this extension as a guide on
how to write authentication backends and models in lux.
"""
from pulsar.api import BadRequest, Http401, PermissionDenied
from pulsar.utils.slugify import slugify

from lux.core import Parameter, LuxExtension, UserMixin
from lux.models import ValidationError
import lux.utils.token as jwt

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
        Parameter('CHECK_USERNAME', 'lux.ext.auth:check_username',
                  'Dotted path to username validation function'),
        # TOKENS
        Parameter('JWT_ALGORITHM', 'HS512', 'Signing algorithm')
    ]

    def on_config(self, app):
        self.require(app, 'lux.ext.odm')
        if not app.config['PASSWORD_SECRET_KEY']:
            app.config['PASSWORD_SECRET_KEY'] = app.config['SECRET_KEY']

    def on_request(self, app, request):
        auth = request.get('HTTP_AUTHORIZATION')
        user = request.cache.get('user')
        if auth and user.is_anonymous():
            self.authorize(request, auth)

    def on_token(self, app, request, token, user):
        if user and user.is_authenticated():
            token['username'] = user.username
            token['user_id'] = user.id
            token['name'] = user.full_name

    def api_sections(self, app):
        return (UserCRUD(),
                TokenCRUD(),
                Authorization(),
                GroupCRUD(),
                PermissionCRUD(),
                RegistrationCRUD(),
                PasswordsCRUD(),
                MailingListCRUD(),
                UserRest())

    def authorize(self, request, auth):
        """Authorize claim

        :param auth: a string containing the authorization information
        """
        user = None
        try:
            try:
                auth_type, key = auth.split(None, 1)
            except ValueError:
                raise BadRequest('Invalid Authorization header') from None
            auth_type = auth_type.lower()
            if auth_type == 'bearer':
                token = self.get_token(request, key)
                if not token:
                    raise BadRequest
                request.cache.token = token
                user = token.user
            elif auth_type == 'jwt':
                token = self.decode_token(request, key)
                request.cache.token = token
                user = self.service_user(request)
        except (Http401, BadRequest, PermissionDenied):
            raise
        except Exception:
            request.app.logger.exception('Could not authorize')
            raise BadRequest from None
        else:
            if user:
                request.cache.user = user

    def decode_jwt(self, request, token, key=None,
                   algorithm=None, **options):
        algorithm = algorithm or request.config['JWT_ALGORITHM']
        try:
            return jwt.decode(token, key=key, algorithm=algorithm,
                              options=options)
        except jwt.ExpiredSignature:
            request.app.logger.warning('JWT token has expired')
            raise Http401('Token')
        except jwt.DecodeError as exc:
            request.app.logger.warning(str(exc))
            raise BadRequest

    def decode_token(self, request, token):
        payload = self.decode_jwt(request, token, verify_signature=False)
        secret = self.secret_from_jwt_payload(request, payload)
        return self.decode_jwt(request, token, secret)


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


class ServiceUser(UserMixin):

    def __init__(self, token=None):
        self.token = token

    def is_superuser(self):
        return self.is_authenticated()

    def is_authenticated(self):
        return bool(self.token)

    def is_anonymous(self):
        return True

    def is_active(self):
        return False


def jwt_token(app, application_id):
    payload = dict(
        application_id=application_id
    )
