'''
This extension does not provide any middleware but it is required
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

     ANGULAR_UI_ROUTER = True

There are two different ways to serve html. The default way is to serve without
the use of angular `ui-router`_, in which case urls load the whole html5
document each time they are accessed.

.. _spa-router:

UI-Router
=============

When switching :setting:`ANGULAR_UI_ROUTER` to ``True``, each page served by
an angular :class:`.Router` is managed, in javascript, by the `ui-router`_ as
a single page application.


.. _AngularJS: https://angularjs.org/
.. _`ui-router`: https://github.com/angular-ui/ui-router
'''
import lux
from lux import Parameter, RouterParam

from pulsar.apps.wsgi import MediaMixin, Html, route
from pulsar.utils.httpurl import urlparse
from pulsar.utils.html import escape

from .ui import add_css


def add_ng_modules(doc, modules):
    if modules:
        ngmodules = set(doc.jscontext.get('ngModules', ()))
        ngmodules.update(modules)
        doc.jscontext['ngModules'] = tuple(ngmodules)


def get_api_info(router, app):
    '''The api name for this :class:`.Router`
    '''
    base = app.config['API_URL']
    if router.api_url:
        return {'url': base, 'name': router.api_url}


class Extension(lux.Extension):

    _config = [
        Parameter('HTML5_NAVIGATION', False,
                  'Enable Html5 navigation', True),
        Parameter('ANGULAR_UI_ROUTER', 'lux.ui.router',
                  'Enable Angular ui-router'),
        Parameter('ANGULAR_VIEW_ANIMATE', False,
                  'Enable Animation of ui-router views.'),
        Parameter('NGMODULES', [], 'Angular module to load')
    ]

    def on_html_document(self, app, request, doc):
        router = html_router(request.app_handler)

        if not router:
            return

        doc.body.data({'ng-model': 'page',
                       'ng-controller': 'Page',
                       'page': ''})
        jscontext = doc.jscontext
        #
        add_ng_modules(doc, app.config['NGMODULES'])

        # Use HTML5 navigation and angular router
        if app.config['HTML5_NAVIGATION']:
            app.require('lux.extensions.rest')
            doc.head.meta.append(Html('base', href="/"))

            uirouter = app.config['ANGULAR_UI_ROUTER']

            if router and uirouter and request.cache.uirouter is not False:
                # The angular root for this router
                add_ng_modules(doc, ('ui.router',))
                root = angular_root(app, router)
                if not hasattr(root, '_angular_sitemap'):
                    root._angular_sitemap = {'hrefs': [],
                                             'pages': {},
                                             'uiRouter': uirouter}
                    add_to_sitemap(root._angular_sitemap, app, doc, root)
                doc.jscontext.update(root._angular_sitemap)

        else:

            add_ng_modules(doc, router.uimodules)

        if router:
            doc.jscontext['page'] = router_href(app, router.full_route)

    def context(self, request, context):
        if request.config['HTML5_NAVIGATION']:
            router = html_router(request.app_handler)
            if router:
                context['html_main'] = self.uiview(request, context)

    def uiview(self, request, context):
        '''Wrap the ``main`` html with a ``ui-view`` container.
        Add animation class if specified in :setting:`ANGULAR_VIEW_ANIMATE`.
        '''
        app = request.app
        main = context.get('html_main', '')
        main = Html('div', main, cn='hidden', id="seo-view")
        div = Html('div', main, cn='angular-view')
        animate = app.config['ANGULAR_VIEW_ANIMATE']
        if animate:
            add_ng_modules(request.html_document, ('ngAnimate',))
            div.addClass(animate)
        div.data('ui-view', 'main')
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


def state_template(self, app):
        '''Template used when in html5 mode
        '''
        div = Html('div', cn=self.angular_view_class)
        div.data({'compile-html': ''})
        return div.render()


class HtmlRouter(lux.HtmlRouter):

    def state_template(self, app, router):
        '''Template for ui-router state associated with this router.
        '''
        pass

    def state_template_url(self, app, router):
        pass

    def get_controller(self, app, router):
        pass

    def angular_page(self, app, router, page):
        '''Callback for adding additional data to angular page object
        '''
        pass


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

    # Set the angukar router
    if isinstance(router, HtmlRouter):
        angular = router

    name = router.name
    if parent:
        name = '%s_%s' % (parent, name)

    page = {'url': path,
            'name': name,
            'parent': parent}

    if angular:
        page.update({'template': angular.state_template(app, router),
                     'templateUrl': angular.state_template_url(app, router),
                     'controller': angular.get_controller(app, router)})
        angular.angular_page(app, router, page)

    sitemap['hrefs'].append(name)
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
            sitemap['hrefs'].append(rpath)
            sitemap['pages'][rpath] = page
