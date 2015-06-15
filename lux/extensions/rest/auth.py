from datetime import datetime, timedelta

from pulsar.apps.wsgi import Json

import lux

from .user import UserMixin


class Anonymous(UserMixin):

    def is_authenticated(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return 0


class AuthBackend(lux.Extension):
    '''Interface for extension supporting restful methods
    '''
    # HTTP Response methods
    def login_response(self, request, user):  # pragma    nocover
        '''Login a user and return a JSON response
        '''
        pass

    def logout_response(self, request, user):  # pragma    nocover
        '''Logout a user and return a JSON response
        '''
        pass

    def signup_response(self, request, user):   # pragma    nocover
        '''After a new ``user`` has signed up, return the response.
        '''
        pass

    def password_changed_response(self, request, user):
        '''JSON response after a password change
        '''
        return Json({'success': True,
                     'message': 'password changed'}).http_response(request)

    def inactive_user_login_response(self, request, user):
        '''JSON response when a non active user logs in
        '''
        pass

    # Internal Methods
    def authenticate(self, request, **params):  # pragma    nocover
        '''Authenticate user'''
        pass

    def create_user(self, request, **kwargs):  # pragma    nocover
        '''Create a standard user.'''
        pass

    def create_superuser(self, request, **kwargs):  # pragma    nocover
        '''Create a user with *superuser* permissions.'''
        pass

    def get_user(self, request, **kwargs):  # pragma    nocover
        '''Retrieve a user.'''
        pass

    def create_token(self, request, user, **kwargs):  # pragma    nocover
        '''Create an athentication token for ``user``'''
        pass

    def request(self, request):  # pragma    nocover
        '''Request middleware. Most backends implement this method
        '''
        pass

    def has_permission(self, request, target, level):  # pragma    nocover
        '''Check if the given request has permission over ``target``
        element with permission ``level``
        '''
        pass

    def anonymous(self):
        '''Anonymous User
        '''
        return Anonymous()

    def session_expiry(self, request):
        '''Expiry for a session or a token
        '''
        session_expiry = request.config['SESSION_EXPIRY']
        if session_expiry:
            return datetime.now() + timedelta(seconds=session_expiry)

    def user_agent(self, request, max_len=80):
        agent = request.get('HTTP_USER_AGENT')
        return agent[:max_len] if agent else ''
