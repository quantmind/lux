"""Authentication backend"""
from pulsar import Http404, BadRequest

from lux.extensions import auth
from lux.extensions import rest

from .multi import get_application


class ServiceUser(rest.ServiceUser):

    def __init__(self, request):
        super().__init__(request)
        self.application = request.cache.application
        request.cache.application_id = request.cache.application.id

    def __repr__(self):
        if self.is_authenticated():
            return '%s - RootUser' % self.application.name
        else:
            return 'anonymous'

    @property
    def application_id(self):
        return self.application.id


class AuthBackend(auth.TokenBackend):
    """Handle multiple applications
    """
    service_user = ServiceUser

    def request(self, request):
        '''Check for ``HTTP_AUTHORIZATION`` header and if it is available
        and the authentication type if ``bearer`` try to perform
        authentication using JWT_.
        '''
        super().request(request)
        user = request.cache.user
        if user.is_anonymous() and not isinstance(user, ServiceUser):
            admin_id = request.config['MASTER_APPLICATION_ID']
            app_id = request.get('HTTP_X_APPLICATION_ID', admin_id)
            try:
                app = get_application(request.app, id=app_id)
            except Http404:
                if request.method == 'OPTIONS':
                    return
            request.cache.application = app
            request.cache.user = self.service_user(request)

    def create_user(self, request, application_id=False, **kw):
        if 'application_id' not in kw:
            user = request.cache.user
            if user:
                kw['application_id'] = user.application_id
            else:
                kw['application_id'] = request.config['MASTER_APPLICATION_ID']
        return super().create_user(request, **kw)

    def secret_from_jwt_payload(self, request, payload):
        app_id = payload.get("id")
        if not app_id:
            raise BadRequest('Missing application id in JWT payload')
        app_domain = get_application(request.app, app_id)
        request.cache.application = app_domain
        return app_domain.secret
