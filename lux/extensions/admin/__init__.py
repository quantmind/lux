'''Admin interface for a site.

This extension requires the :mod:`~lux.extensions.sessions` extension.
'''
import lux
from lux import Parameter

from pulsar import ImproperlyConfigured, Http404
from .ui import add_css


class Extension(lux.Extension):
    _config = [
        Parameter('ADMIN_URL', 'admin/',
                  'the base url for the admin site'),
        Parameter('ADMIN_THEME', 'default',
                  'Theme for the admin site')
    ]

    def middleware(self, app):
        if not app.auth_backend:
            raise ImproperlyConfigured('sessions backend required')
        path = app.config['ADMIN_URL']
        app.admin = Admin(path, response_wrapper=require_superuser)
        return [app.admin]

    def context(self, request, context):
        app_handler = request.app_handler
        if app_handler and app_handler.has_parent(request.app.admin):
            links = request.app.admin.links
            context['theme'] = request.config['ADMIN_THEME']
            if links:
                context['admin_links'] = [{'name': l[0],
                                           'href': l[1].full_route.path}
                                          for l in links]


class Admin(lux.Router):
    '''Admin for a site
    '''
    links = None

    def add(self, link, router):
        '''Add a new router to the admin and insert the link in the
        list of links'''
        self.add_child(router)
        links = self.links
        if not links:
            self.links = links = []
        links.append((link, router))

    def get(self, request):
        links = [{'name': l[0], 'href': l[1].path()} for l in self.links]
        ctx = {'links': links}
        return request.app.html_response(request, 'admin.html',
                                         jscontext=ctx,
                                         title='%s - Admin')

def require_superuser(handler, request):
    user = request.cache.user
    super_user = getattr(user, 'is_superuser', False)
    if hasattr(super_user, '__call__'):
        super_user = super_user()
    if not super_user:
        raise Http404
    return handler(request)
