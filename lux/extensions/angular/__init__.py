'''
This extension does not provide any middleware per-se but it is required
when using :ref:`lux.js <jsapi>` javascript module and
provides the link between AngularJS_ and Python.

**Required extensions**: :mod:`lux.extensions.ui`

Usage
=========

Include ``lux.extensions.angular`` into the :setting:`EXTENSIONS` list in your
:ref:`config file <parameters>`::

    EXTENSIONS = [
        ...
        'lux.extensions.ui',
        'lux.extensions.angular'
        ...
        ]

     HTML5_NAVIGATION = True


.. _AngularJS: https://angularjs.org/
.. _`ui-router`: https://github.com/angular-ui/ui-router
'''
from urllib.parse import urlparse

import lux
from lux import Parameter

from pulsar import Http404
from pulsar.apps.wsgi import Html

from .ui import add_css
from .components import grid


__all__ = ['add_css', 'grid', 'add_ng_modules']


def add_ng_modules(doc, modules):
    if modules:
        if not isinstance(modules, (list, tuple)):
            modules = (modules,)
        ngmodules = set(doc.jscontext.get('ngModules', ()))
        ngmodules.update(modules)
        doc.jscontext['ngModules'] = tuple(ngmodules)


def ng_template(request, *args):
    '''Check if a request is for a angular template

    An angular template request has the template=ui
    query string in it
    '''
    if not (request.config.get('HTML5_NAVIGATION') and
            request.url_data.get('template') == 'ui'):
        return
    urlargs = request.urlargs
    if urlargs:
        urlargs = urlargs.copy()
        for arg in args:
            if urlargs.pop(arg) != arg:
                raise Http404
    if not urlargs:
        return True


UIROUTER = ('lux.ui.router',)


class Extension(lux.Extension):

    _config = [
        Parameter('HTML5_NAVIGATION', False,
                  'Enable Html5 navigation', True),
        Parameter('ANGULAR_VIEW_ANIMATE', False,
                  'Enable Animation of ui-router views.'),
        Parameter('NGMODULES', [], 'Angular module to load')
    ]

    def on_html_document(self, app, request, doc):
        router = html_router(request.app_handler)

        if not router:
            return
        #
        add_ng_modules(doc, app.config['NGMODULES'])

        # Use HTML5 navigation and angular router
        if app.config['HTML5_NAVIGATION']:
            add_ng_modules(doc, UIROUTER)
            root = angular_root(app, router)

            doc.body.data({'ng-model': 'page',
                           'ng-controller': 'Page',
                           'page': ''})

            doc.head.meta.append(Html('base', href="/"))

            if not hasattr(root, '_angular_sitemap'):
                root._angular_sitemap = {'states': [], 'pages': {}}
                add_to_sitemap(root._angular_sitemap, app, doc, root)
            doc.jscontext.update(root._angular_sitemap)
            doc.jscontext['page'] = router.state
        else:
            add_ng_modules(doc, router.uimodules)

    def context(self, request, context):
        router = html_router(request.app_handler)
        if request.config['HTML5_NAVIGATION'] and router:
            pages = request.html_document.jscontext['pages']
            page = pages.get(router.state)
            context['html_main'] = self.uiview(request, context, page)

    def uiview(self, request, context, page):
        '''Wrap the ``main`` html with a ``ui-view`` container.
        Add animation class if specified in :setting:`ANGULAR_VIEW_ANIMATE`.
        '''
        app = request.app
        main = context.get('html_main', '')
        if 'templateUrl' in page or 'template' in page:
            main = Html('div', main, cn='hidden', id="seo-view")
        div = Html('div', main, cn='angular-view')
        animate = app.config['ANGULAR_VIEW_ANIMATE']
        if animate:
            add_ng_modules(request.html_document, ('ngAnimate',))
            div.addClass(animate)
        div.data('ui-view', '')
        return div.render()


def html_router(router):
    if isinstance(router, lux.HtmlRouter):
        return router


def angular_root(app, router):
    '''The root angular router
    '''
    if not hasattr(router, '_angular_root'):
        if angular_compatible(app, router, router.parent):
            router._angular_root = angular_root(app, router.parent)
        else:
            router._angular_root = router
    return router._angular_root


def angular_compatible(app, router1, router2):
    router1 = html_router(router1)
    router2 = html_router(router2)
    if router1 and router2:
        templ1 = router1.get_html_body_template(app)
        templ2 = router2.get_html_body_template(app)
        return templ1 == templ2
    return False


def router_href(app, route):
    url = '/'.join(_angular_route(route))
    if url:
        url = '/%s' % url if route.is_leaf else '/%s/' % url
    else:
        url = '/'
    site_url = app.config['SITE_URL']
    if site_url:
        p = urlparse(site_url + url)
        return p.path
    else:
        return url


def _angular_route(route):
    for is_dynamic, val in route.breadcrumbs:
        if is_dynamic:
            c = route._converters[val]
            yield '*%s' % val if c.regex == '.*' else ':%s' % val
        else:
            yield val


def add_to_sitemap(sitemap, app, doc, router, parent=None, angular=None):
    # path for the current router
    path = router_href(app, router.full_route)

    # Set the angular router if the router has a callable method
    # named angular_page
    if (hasattr(router, 'angular_page') and
            hasattr(router.angular_page, '__call__')):
        angular = router

    name = router.name
    if parent:
        name = '%s_%s' % (parent, name)

    router.state = name

    page = {'url': path, 'name': name}

    if angular:
        angular.angular_page(app, router, page)

    sitemap['states'].append(name)
    sitemap['pages'][name] = page
    add_ng_modules(doc, router.uimodules)
    #
    # Loop over children routes
    for child in router.routes:
        add_to_sitemap(sitemap, app, doc, child, name, angular)

    # Add redirect to folder page if required
    return
    if path.endswith('/') and path != '/':
        rpath = path[:-1]
        if rpath not in sitemap['pages']:
            page = {'url': rpath,
                    'redirectTo': path}
            sitemap['states'].append(rpath)
            sitemap['pages'][rpath] = page
