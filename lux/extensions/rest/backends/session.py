import time

from pulsar import PermissionDenied, ImproperlyConfigured

from .. import AuthBackend
from .mixins import jwt, SessionBackendMixin
from .registration import RegistrationMixin
from .permissions import PemissionsMixin


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


class CsrfBackend(AuthBackend):
    """A backend for Cross-Site Request Forgery prevention.

    This backend is aimed at html web applications with form sending requests
    It requires the :class:`.SessionBackend`.
    """
    CSRF_SET = frozenset(('GET', 'HEAD', 'OPTIONS'))

    def on_form(self, app, form):
        """Handle CSRF on form
        """
        request = form.request
        param = app.config['CSRF_PARAM']
        if (param and form.is_bound and
                request.method not in self.CSRF_SET):
            token = form.rawdata.get(param)
            self.validate_csrf_token(request, token)

    def on_html_document(self, app, request, doc):
        if request.method in self.CSRF_SET:
            cfg = app.config
            param = cfg['CSRF_PARAM']
            if param:
                csrf_token = self.csrf_token(request)
                if csrf_token:
                    doc.head.add_meta(name="csrf-param", content=param)
                    doc.head.add_meta(name="csrf-token", content=csrf_token)

    # CSRF
    def csrf_token(self, request):
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        session = request.cache.session
        if session:
            expiry = request.config['CSRF_EXPIRY']
            secret_key = request.config['SECRET_KEY']
            return jwt.encode({'session': session.get_key(),
                               'exp': time.time() + expiry},
                              secret_key)

    def validate_csrf_token(self, request, token):
        bad_token = request.config['CSRF_BAD_TOKEN_MESSAGE']
        expired_token = request.config['CSRF_EXPIRED_TOKEN_MESSAGE']
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        if not token:
            raise PermissionDenied(bad_token)
        try:
            secret_key = request.config['SECRET_KEY']
            token = jwt.decode(token, secret_key)
        except jwt.ExpiredSignature:
            raise PermissionDenied(expired_token)
        except Exception:
            raise PermissionDenied(bad_token)
        else:
            if token['session'] != request.cache.session.get_key():
                raise PermissionDenied(bad_token)
