'''Permissions are controlled by a :class:`PermissionHandler`

.. _api-permission-codes:

Permissions Codes
~~~~~~~~~~~~~~~~~~~~~~~~~~

* ``VIEW`` This is the lowest level of permission. Value ``10``.
* ``CHANGE`` Allows to change/modify objects. Value ``20``.
* ``COPY`` Allows to copy objects into new ones. Value ``25``.
* ``ADD`` Allows to add new objects. Value ``30``.
'''
from pulsar.apps.wsgi import authorization_middleware
from pulsar import PermissionDenied, coroutine_return

__all__ = ['PermissionsCodes',
           'AuthBackend',
           'AuthenticationError',
           'LoginError',
           'PermissionHandler']


# Main permission flags
# the higher the number the more restrictive the permission is
class PermissionsCodes:
    '''The higher the number the more permissions are granted.'''
    NONE = 0    # always a permission denied
    READ = 10   # read/view stuff
    UPDATE = 20
    CREATE = 30
    REMOVE = 40

    def __init__(self):
        self.codes = {}
        for name in dir(self):
            if name == name.upper():
                value = getattr(self, name)
                self.codes[name.lower()] = getattr(self, name)


class AuthenticationError(ValueError):
    pass


class LoginError(RuntimeError):
    pass


class LogoutError(RuntimeError):
    pass


class SimpleRobots(object):

    def __init__(self, settings):
        pass

    def __call__(self, request):
        if request.has_permission(user=None):
            #if not self.page or self.page.insitemap:
            return 'ALL'
        return 'NONE,NOARCHIVE'


class AuthBackend(object):
    '''Interface for authentication backends.

    An Authentication backend manage authentication, login, logout and
    several other activities which are required for managing users of
    a web site.
    '''
    def authenticate(self, request, user, **params):
        '''Authenticate a user'''
        pass

    def login(self, request, user):
        pass

    def logout(self, request, user):
        pass

    def get_user(self, request, *args, **kwargs):
        '''Retrieve a user.

        This method can raise an exception if the user could not be found,
        or return ``None``.
        '''
        pass

    def create_user(self, request, *args, **kwargs):
        '''Create a standard user.'''
        pass

    def create_superuser(self, request, *args, **kwargs):
        '''Create a user with *superuser* permissions.'''
        pass

    def request_middleware(self):
        return ()

    def post_data_middleware(self):
        return ()

    def response_middleware(self):
        return ()

    def has_permission(self, request, action, model):
        '''Check for permission on a model.'''
        pass


class PermissionHandler(object):
    '''Base class for permissions handlers.

    :param settings: a settings dictionary.
    :param auth_backends: set the :attr:`auth_backends`. If not provided, the
        :attr:`auth_backends` will be created by the :meth:`default_backends`.
    :param requires_login: if ``True``, an authenticated user is always
        required.

    .. attribute:: auth_backends

        The list of :class:`AuthBackend`.

    .. attribute:: permission_codes

        A dictionary for mapping numeric codes into
        :ref:`permissions names <api-permission-codes>`. The higher the
        numeric code the more restrictive the permission is.
    '''
    AuthenticationError = AuthenticationError

    def __init__(self):
        self.auth_backends = []
        self.codes = PermissionsCodes()

    def post_data_middleware(self):
        middleware = []
        for b in self.auth_backends:
            try:
                middleware.extend(b.post_data_middleware())
            except:
                pass
        return middleware

    def add_code(self, name, code):
        '''Add a permission code to the list'''
        code = int(code)
        if code > 0:
            self.codes[name.lower()] = code
            return code

    def permission_choices(self):
        c = self.permission_codes
        return ((k, c[k]) for k in sorted(c))

    def get_user(self, request, *args, **kwargs):
        '''Retrieve a ``user`` by looping through all available
        :attr:`auth_backends`.

        This method is safe and returns ``None`` if no ``user``
        could be found.
        '''
        for b in self.auth_backends:
            try:
                user = yield b.get_user(request, *args, **kwargs)
            except Exception:
                continue
            if user is not None:
                coroutine_return(user)

    def authenticate_and_login(self, request, user, **params):
        ''':meth:`authenticate` and :meth:`login` a ``user``. Raises
an :class:`AuthenticationError` if the ``user`` could not be authenticated.'''
        if user.is_active:
            user = self.authenticate(request, user, **params)
            user = yield self.login(request, user)
            coroutine_return(user)
        else:
            raise AuthenticationError('%s is not active' % user)

    def authenticate(self, request, user, **params):
        '''Authenticate a ``user``.

        Raises an :class:`AuthenticationError` if the ``user`` could
        not be authenticated.
        '''
        for b in self.auth_backends:
            try:
                auth = b.authenticate(request, user, **params)
            except AuthenticationError:
                raise
            except Exception:
                # if not an AuthenticationError try the next backend
                continue
            if auth is not None:
                return auth
        raise AuthenticationError('Could not authenticate')

    def login(self, request, user):
        '''Login a ``user``.

        Raises an :class:`LoginError` if the ``user`` could not login.'''
        for b in self.auth_backends:
            try:
                u = yield b.login(request, user)
            except Exception:
                continue
            if u is not None:
                coroutine_return(u)
        raise LoginError('Could not login')

    def logout(self, request):
        '''Logout user'''
        for b in self.auth_backends:
            try:
                u = yield b.logout(request)
            except Exception:
                continue
            if u is not None:
                coroutine_return(u)
        raise LogoutError('Could not logout')

    def create_user(self, request, *args, **kwargs):
        for b in self.auth_backends:
            try:
                user = yield b.create_user(request, *args, **kwargs)
                if user is not None:
                    coroutine_return(user)
            except Exception:
                continue

    def create_superuser(self, request, *args, **kwargs):
        for b in self.auth_backends:
            try:
                user = yield b.create_superuser(request, *args, **kwargs)
                if user is not None:
                    coroutine_return(user)
            except Exception as exc:
                continue

    def set_password(self, user, password):
        '''Loop though all :attr:`athentication_backends` and try to set
a new *password* for *user*. If it fails on all backends a ``ValueError``
is raised. User shouldn't need to override this function, instead they should
implement the :meth:`set_password` method on their authentication backend
if needed.

:param user: a user instance
:param password: the row password to assign to user.
'''
        success = False
        for b in self.auth_backends:
            try:
                b.set_password(user, password)
                success = True
            except:
                continue
        if not success:
            raise ValueError('Could not set password for user %s' % user)

    def authenticated(self, request, instance, default=False):
        if getattr(instance, 'requires_login', default):
            return request.user.is_authenticated()
        else:
            return True

    def has(self, request, action, model):
        '''Check for permissions for a given request.

:param request: a :class:`lux.WsgiRequest`.
:param action: code for permissions.
:param model: optional model for which we require permission.
:param user: optional user for which we require permission.
'''
        for b in self.auth_backends:
            has = b.has_permission(request, action, model)
            if has in (True, False):
                return has
        return True

    def level(self, model, instance, user):
        '''The level of permission for *user* on *instance*.'''
        return DELETE

    def add_model(self, model):
        pass

    def header_authentication_middleware(self, environ, start_response):
        '''A middleware for basic Authentication via Headers.

        Add as first request middleware if you want to support this.
        '''
        authorization_middleware(environ, start_response)
        auth = environ.get('HTTP_AUTHORIZATION')
        if auth:
            environ['user'] = self.authenticate(environ,
                                                username=auth.username,
                                                password=auth.password)


def authenticated_view(f):
    '''Decorator which check if a request is authenticated'''
    def _(self, request, *args, **kwargs):
        user = request.user
        if user and user.is_authenticated() and user.is_active:
            return f(self, request, *args, **kwargs)
        else:
            raise PermissionDenied()

    return _
