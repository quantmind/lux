'''Admin interface for a site.

This extension requires the :mod:`~lux.extensions.sessions` extension.

API
=======

Router
------------

.. autoclass:: Router
   :members:
   :member-order: bysource

'''
import lux
from lux import Parameter, Html

from pulsar import ImproperlyConfigured, Http404
from .ui import add_css, collapse_width


class Extension(lux.Extension):
    _config = [
        Parameter('ADMIN_URL', 'admin/',
                  'the base url for the admin site'),
        Parameter('ADMIN_SERVE', True,
                  'Include the admin router in the wsgi middleware'),
        Parameter('ADMIN_THEME', 'default',
                  'Theme for the admin site')
    ]

    def middleware(self, app):
        if not app.auth_backend:
            raise ImproperlyConfigured('Authentication backend required')
        path = app.config['ADMIN_URL']
        app.admin = Router(path, name='admin',
                           response_wrapper=require_superuser)
        if app.config['ADMIN_SERVE']:
            return [app.admin]


class Router(lux.Router):
    '''A specialised Router for an admin site

    The admin root router can be access from the application ``admin``
    attribute::

        def handler(request):
            admin = request.app.admin

    '''
    template_name = lux.RouterParam('html')
    in_nav = True
    target = None

    def get(self, request):
        path = request.path
        sitemap, page = self.sitemap(path)
        if self.root.path() == path and sitemap:
            return request.redirect(sitemap[0]['href'])
        else:
            ctx = {'sitemap': sitemap,
                   'page': page,
                   'collapse_width': collapse_width,
                   'theme': request.config['ADMIN_THEME']}
            return self.html_response(request, ctx)

    def sitemap(self, path):
        '''Build the sitemap for this router.
        '''
        root = self.root
        parent = {'href': root.path(),
                  'name': root.name,
                  'target': '_self'}
        sitemap, page = _sitemap(root, [parent], path, children=True)
        page = parent if path == parent['href'] else page
        return sitemap, page

    def html_response(self, request, ctx):
        '''Build the html response
        '''
        app = request.app
        context = {'page_footer': app.template('footer.html')}
        return app.html_response(request, 'admin.html', jscontext=ctx,
                                 context=context, title='%s - Admin')

    def instance_url(self, request, instance):
        '''Return the url for editing the ``instance``
        '''
        pass

    def wrap_html(self, request, html, span=12):
        '''Default wrapper for html loaded via angular
        '''
        return Html('div',
                    Html('div', html, cn='col-sm-%d' % span),
                    cn='row').render(request)


def _sitemap(self, parents, path, children=False):
    links = []
    page = None
    root = self
    getmany = False
    apiname = self.name
    for router in self.routes:
        if children:
            root = router
            getmany = True
            apiname = router.name
        # In navigation
        if getattr(router, 'in_nav', False):
            vars = router.route.ordered_variables or None
            if vars:
                params = dict(((v, ':%s' % v) for v in vars))
                href = router.path(**params)
            else:
                href = router.path()
            template_router = root.get_route(router.template_name)
            link = {'href': href,
                    'vars': vars,
                    'name': router.name,
                    'title': getattr(router, 'title', router.name),
                    'parents': parents,
                    'api': apiname,
                    'getmany': getmany,
                    'target': getattr(router, 'target', None)}
            if template_router:
                link.update({'template_url': template_router.path(),
                             'controller': template_router.get_controller()})
            if href == path:
                page = link
                parents[-1]['active'] = True
            if children:
                nparents = [link]
                nparents.extend(parents)
                nparents = list(reversed(nparents))
                children, pg = _sitemap(router, nparents, path)
                page = page or pg
            if children:
                parent = {'links': children}
                parent.update(link)
                links.append(parent)
            else:
                links.append(link)
    return links, page


def require_superuser(handler, request):
    user = request.cache.user
    super_user = getattr(user, 'is_superuser', False)
    if hasattr(super_user, '__call__'):
        super_user = super_user()
    if not super_user:
        raise Http404
    return handler(request)
