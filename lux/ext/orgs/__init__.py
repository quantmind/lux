from pulsar.api import Http404

from lux.core import Parameter, is_html
from lux.ext import auth

from .events import AuthEventsMixin
from .rest import UserCRUD, UserRest, OrganisationCRUD
# from .views import UserSettings, UserView
from .ownership import get_owned_model


class Extension(auth.Extension, AuthEventsMixin):
    _config = [
        Parameter('ORGANISATION_ADMIN_PERMISSION',
                  'organisation:{username}:admin',
                  'Format string for organisation admin groups'),
        Parameter('AUTHENTICATED_USER_GROUP',
                  'users',
                  'Name of the group containing all authenticated users')
    ]

    #def middleware(self, app):
    #    # user and organisation plugins in Html mode
    #    if is_html(app) and has_plugin(app, 'users'):
    #        orgs = has_plugin(app, 'organisations')
    #        yield UserSettings('/settings')
    #        yield UserView(orgs)

    def api_sections(self, app):
        return (
            UserRest(),
            UserCRUD(),
            OrganisationCRUD()
        )

    def on_query(self, app, query):
        try:
            target = get_owned_model(app, query.model.uri)
            query.filters['owner'] = target.filter
        except Http404:
            pass

    def on_html_document(self, app, request, doc):
        '''Add admin user entry to the javascript context
        '''
        if request.cache.get('session'):
            backend = request.cache.auth_backend
            user = request.cache.user
            if user and user.is_authenticated():
                user = dict(user)
                user['admin'] = backend.has_permission(
                    request, 'site:admin', 'read')
                doc.jscontext['user'] = user
