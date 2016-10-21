"""Backends for Browser based Authentication
"""
import time
from functools import wraps

from pulsar import Http401, PermissionDenied, Http404, HttpRedirect
from pulsar.apps.wsgi import Route, wsgi_request

from lux.utils.date import to_timestamp
from lux.core import app_attribute, backend_action, User

from .store import session_store


NotAuthorised = (Http401, PermissionDenied)


@app_attribute
def exclude_urls(app):
    """urls to exclude from browser sessions
    """
    urls = []
    for url in app.config['SESSION_EXCLUDE_URLS']:
        urls.append(Route(url))
    return tuple(urls)


def session_backend_action(method):
    backend_action(method)

    @wraps(method)
    def _(self, r, *args, **kwargs):
        if wsgi_request(r.environ).cache.skip_session_backend:
            return

        return method(self, r, *args, **kwargs)

    return _


class SessionBackend:
    """SessionBackend is used when the client is a web browser

    It maintain a session via a cookie key
    """
    @session_backend_action
    def authenticate(self, request, **data):
        api = request.api
        response = api.authorizations.post(json=data, jwt=True)
        token = response.json()
        request.cache.session = self._create_session(request, token)
        return User(response.json())

    @session_backend_action
    def logout(self, request):
        """logout a user
        """
        backend = request.cache.auth_backend
        session_store(request).delete(request.cache.session.id)
        request.cache.user = backend.anonymous(request)
        request.cache.session = self._create_session(request)

    @session_backend_action
    def get_permissions(self, request, resources, actions=None):
        return self._get_permissions(request, resources, actions)

    @session_backend_action
    def has_permission(self, request, resource, action):
        """Implement :class:`~AuthBackend.has_permission` method
        """
        data = self._get_permissions(request, resource, action)
        resource = data.get(resource)
        if resource:
            return resource.get(action, False)
        return False

    def request(self, request):
        path = request.path[1:]
        for url in exclude_urls(request.app):
            if url.match(path):
                request.cache.skip_session_backend = True
                return

        key = request.config['SESSION_COOKIE_NAME']
        session_key = request.cookies.get(key)
        session = None
        if session_key:
            session = session_store(request).get(session_key.value)
        if not session:
            session = self._create_session(request)
        request.cache.session = session
        user = session.user
        if user:
            auth = self.authorization(request)
            auth.head(token=user.token)
            if user.token:
                auth = self.authorization(request)
                try:
                    auth.head(token=user.token)
                except NotAuthorised:
                    handle_401(request, user)
            request.cache.user = user

    @session_backend_action
    def response(self, response):
        request = wsgi_request(response.environ)
        session = request.cache.session
        if session:
            if response.can_set_cookies():
                key = request.config['SESSION_COOKIE_NAME']
                session_key = request.cookies.get(key)
                id = session.id
                if not session_key or session_key.value != id:
                    response.set_cookie(key, value=str(id), httponly=True,
                                        expires=session.expiry)
            return session_store(request).save(session)
        return response

    # INTERNALS
    def _create_session(self, request, token=None):
        """Create a new Session object"""
        expiry = None
        if token:
            expiry = to_timestamp(token.get('expiry'))
            token = token['id']
        if not expiry:
            seconds = request.config['SESSION_EXPIRY']
            expiry = time.time() + seconds
        return session_store(request).create(expiry=expiry,
                                             token=token)

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
