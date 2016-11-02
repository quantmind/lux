from lux.core import Parameter
from lux.extensions import auth

from .events import AuthEventsMixin
from .rest import UserCRUD, UserRest, OrganisationCRUD
from .views import UserSettings, UserView

from ..applications import has_plugin, is_html


class Extension(auth.Extension, AuthEventsMixin):
    _config = [
        Parameter('ORGANISATION_ADMIN_PERMISSION',
                  'organisation:{username}:admin',
                  'Format string for organisation admin groups'),
        Parameter('AUTHENTICATED_USER_GROUP',
                  'users',
                  'Name of the group containing all authenticated users')
    ]

    def on_config(self, app):
        self.require(app, 'lux.extensions.applications')

    def middleware(self, app):
        # user and organisation plugins in Html mode
        if is_html(app) and has_plugin(app, 'users'):
            orgs = has_plugin(app, 'organisations')
            yield UserSettings('/settings')
            yield UserView(orgs)

    def api_sections(self, app):
        return (UserRest(),
                UserCRUD(),
                OrganisationCRUD())

    def on_html_document(self, app, request, doc):
        '''Add adminuser entry to the javascript context
        '''
        if request.cache.session:
            backend = request.cache.auth_backend
            user = request.cache.user
            if user and user.is_authenticated():
                user = dict(user)
                user['admin'] = backend.has_permission(
                    request, 'site:admin', 'read')
                doc.jscontext['user'] = user
