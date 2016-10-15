"""Backends for Browser based Authentication
"""
import uuid

from pulsar import Http401, PermissionDenied, Http404, HttpRedirect
from pulsar.utils.slugify import slugify

from lux.utils.token import decode

from .mixins import SessionBackendMixin
from .registration import RegistrationMixin
from .. import (AuthenticationError, AuthBackend, session_backend,
                User, Session)


NotAuthorised = (Http401, PermissionDenied)



class SessionBackend(SessionBackendMixin,
                     RegistrationMixin,
                     PemissionsMixin,
                     AuthBackend):
    """SessionBackend is used when the client is a web browser

    It maintain a session via a cookie key
    """
    def create_session(self, request, user=None):
        user = user or request.cache.user
        return self.create_token(request, user,
                                 expiry=self.session_expiry(request))


class ApiSessionBackend(SessionBackendMixin):
    """A browser backend which is a proxy for a REST API backend.

    This backend requires a real cache backend, it cannot work with dummy
    cache and will raise an error.

    All requests are passed to the Rest API ``authorizations`` endpoints

    The workflow for authentication is the following:

    * send request to Rest API for authentication
    * If successful obtain the ``token`` from the response
    * Create the user from decoding the JWT payload
    * Create the session with same id as the token id and set the user as
      session key
    * Save the session in cache and return the original encoded token
    """
    signup_url = 'authorizations/signup'
    """url for signup a user.
    """
    reset_password_url = 'authorizations/reset-password'
    """url for resetting password
    """
    auth_keys_url = 'authorizations/keys'
    """url for authorization keys
    """
    users_url = 'users'

    def _execute_backend_method(self, method, request, *args, **data):
        method = slugify(method)
        if args:
            request.logger.error('Positional arguments not accepted by '
                                 '%s.%s' % (type(self).__name__, method))
        response = request.api.post('authorizations/%s' % method, json=data)
        return response.json()

    def authenticate(self, request, **data):
        response = request.api.post('authorizations', json=data)
        token = response.json().get('token')
        payload = decode(token, verify=False)
        user = User(payload)
        user.encoded = token
        return user

    def signup(self, request, **data):
        """Create a new user from the api
        """
        return request.api.user.signup.post(json=data).json()

    def signup_confirm(self, request, key):
        return request.api.user.signup.post(key)

    def signup_confirmation(self, request, username):
        api = request.app.api(request)
        response = api.post('authorizations/%s' % username)
        return response.json()

    def get_permissions(self, request, resources, actions=None):
        return self._get_permissions(request, resources, actions)

    def has_permission(self, request, resource, action):
        """Implement :class:`~AuthBackend.has_permission` method
        """
        data = self._get_permissions(request, resource, action)
        resource = data.get(resource)
        if resource:
            return resource.get(action, False)
        return False

    def password_recovery(self, request, **params):
        return request.api.post(self.reset_password_url, data=params).json()

    def set_password(self, request, password, user=None, auth_key=None):
        api = request.app.api(request)
        if not auth_key:
            raise AuthenticationError('Missing authentication key')
        url = '%s/%s' % (self.reset_password_url, auth_key)
        data = {'password': password, 'password_repeat': password}
        response = api.post(url, data=data)
        return response.json()

    def confirm_auth_key(self, request, key, **kw):
        try:
            request.api.head('%s/%s' % (self.auth_keys_url, key))
        except Http404:
            return False
        return True

    def create_session(self, request, user=None):
        """Login and return response
        """
        if user:
            user = User(user)
            session = Session(id=user.pop('token_id'),
                              expiry=user.pop('exp'),
                              user=user)
            session.encoded = session.user.pop('encoded')
        else:
            session = Session(id=uuid.uuid4().hex)
        return session

    def get_session(self, request, key):
        """Get the session at key from the cache server
        """
        cache = session_backend(request.app)
        session = cache.get(key)
        if session:
            session = Session(session)
            if session.user:
                user = User(session.user)
                # Check if the token is still a valid one
                try:
                    if not session.encoded:
                        raise Http401
                    request.api.head('authorizations', token=session.encoded)
                except NotAuthorised:
                    handle_401(request, user)
                session.user = user
            return session

    def session_save(self, request, session):
        data = session.all()
        if session.user:
            data['user'] = session.user.all()
        session_backend(request.app).set(session.id, data)

    # INTERNALS
    def _get_permissions(self, request, resources, actions=None):
        if not isinstance(resources, (list, tuple)):
            resources = (resources,)
        query = [('resource', resource) for resource in resources]
        if actions:
            if not isinstance(actions, (list, tuple)):
                actions = (actions,)
            query.extend((('action', action) for action in actions))
        try:
            response = request.api.user.permissions.get(params=query)
        except NotAuthorised:
            handle_401(request)

        return response.json()


def handle_401(request, user=None):
    """When the API respond with a 401 logout and redirect to login
    """
    user = user or request.session.user
    if user.is_authenticated():
        request.cache.auth_backend.logout(request)
        raise HttpRedirect(request.config['LOGIN_URL'])
    else:
        raise Http404
