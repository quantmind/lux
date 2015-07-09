import time

from pulsar import PermissionDenied, ImproperlyConfigured

from lux import Parameter

from .. import AuthBackend
from .mixins import jwt, SessionBackendMixin
from .registration import RegistrationMixin


class SessionBackend(SessionBackendMixin, RegistrationMixin, AuthBackend):

    def create_session(self, request, user=None):
        user = user or request.cache.user
        return self.create_token(request, user,
                                 expiry=self.session_expiry(request))


class CsrfBackend(AuthBackend):
    '''A backend for Cross-Site Request Forgery prevention.

    Can be used on a session backend.
    '''
    _config = [
        Parameter('CSRF_EXPIRY', 60*60,
                  'Cross Site Request Forgery token expiry in seconds.'),
        Parameter('CSRF_PARAM', 'authenticity_token',
                  'CSRF parameter name in forms')
    ]
    REASON_BAD_TOKEN = "CSRF token missing or incorrect"
    CSRF_SET = frozenset(('GET', 'HEAD', 'OPTIONS'))

    def on_form(self, app, form):
        '''Handle CSRF on form
        '''
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
        if not jwt:     # pragma    nocover
            raise ImproperlyConfigured('JWT library not available')
        if not token:
            raise PermissionDenied(self.REASON_BAD_TOKEN)
        try:
            secret_key = request.config['SECRET_KEY']
            token = jwt.decode(token, secret_key)
        except jwt.ExpiredSignature:
            raise PermissionDenied('Expired token')
        except Exception:
            raise PermissionDenied(self.REASON_BAD_TOKEN)
        else:
            if token['session'] != request.cache.session.get_key():
                raise PermissionDenied(self.REASON_BAD_TOKEN)
