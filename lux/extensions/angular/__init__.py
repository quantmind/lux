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


class Extension(lux.Extension):

    _config = [
        Parameter('HTML5_NAVIGATION', True, 'Enable Html5 navigation'),
        Parameter('ANGULAR_UI_ROUTER', False, 'Enable Angular ui-router'),
        Parameter('ANGULAR_VIEW_ANIMATE', False,
                  'Enable Animation of ui-router views.'),
        Parameter('NAVBAR_COLLAPSE_WIDTH', 768,
                  'Width when to collapse the navbar'),
        Parameter('NGMODULES', [], 'Angular module to load')
    ]

    def on_html_document(self, app, request, doc):
        min = '.min' if app.config['MINIFIED_MEDIA'] else ''
        js = app.template('lux.require%s.js' % min)
        doc.head.embedded_js.append(js)
        doc.body.data({'ng-model': 'page',
                       'ng-controller': 'Page',
                       'page': ''})
        jscontext = doc.jscontext
        jscontext['html5mode'] = app.config['HTML5_NAVIGATION']
        navbar = doc.jscontext.get('navbar') or {}
        navbar['collapseWidth'] = app.config['NAVBAR_COLLAPSE_WIDTH']
        jscontext['navbar'] = navbar
        #
        if jscontext['html5mode']:
            doc.head.meta.append(Html('base', href=""))

        add_ng_modules(doc, app.config['NGMODULES'])

    def context(self, request, context):
        router = request.app_handler
        if isinstance(router, Router):
            return router.context(request, context)


class Router(lux.Router, MediaMixin):
    '''A :class:`.Router` for Angular navigation.
    '''
    in_nav = True
    title = None
    api = None
    angular_view_class = RouterParam('angular-view')
    ngmodules = None
    '''Optional list of angular modules to include
    '''
    uirouter = 'lux.ui.router'
    '''Override the :setting:`ANGULAR_UI_ROUTER` setting for this
    :class:`.Router`. If set to ``False`` the `ui-router`_ won't be used
    and the whole html5 document is loaded when accessed.'''
    _sitemap = None

    @property
    def angular_root(self):
        '''The root angular router
        '''
        root = self
        while isinstance(root.parent, Router):
            if (root.html_body_template == root.parent.html_body_template and
                    root.parent.uirouter == root.uirouter):
                root = root.parent
            else:
                break
        return root

    def get_html(self, request):
        return ''

    def context(self, request, context):
        '''This is the only http method implemented.

        If this :class:`.Router` is operating in :ref:`ui mode <spa-router>`,
        this method performs the following tasks:

        * Collets children routers operating in :ref:`ui mode <spa-router>`
          and build the sitemap used by angular `ui-router`_.

            <div id="seo-view" data-ui-main="main" class="hidden">
                $html_main
            </div>
        '''
        app = request.app
        doc = request.html_document
        #
        if request.cache.uirouter is False:
            uirouter = None
        else:
            uirouter = app.config['ANGULAR_UI_ROUTER'] and self.uirouter
        #
        # Using Angular Ui-Router
        if uirouter:
            doc.jscontext.update(self.sitemap(app, doc, uirouter))
            doc.jscontext['page'] = router_href(app, self.full_route)
            context['html_main'] = self.uiview(request, context)
        else:
            add_ng_modules(doc, self.ngmodules)

    def uiview(self, request, context):
        '''Wrap the ``main`` html with a ``ui-view`` container.
        Add animation class if specified in :setting:`ANGULAR_VIEW_ANIMATE`.
        '''
        app = request.app
        main = context.get('html_main', '')
        main = Html('div', main, cn='hidden', id="seo-view")
        div = Html('div', main, cn=self.angular_view_class)
        animate = app.config['ANGULAR_VIEW_ANIMATE']
        if animate:
            add_ng_modules(request.html_document, ('ngAnimate',))
            div.addClass(animate)
        div.data('ui-view', 'main')
        return div.render()

    def state_template(self, app):
        '''Template for ui-router state associated with this router.
        '''
        pass

    def state_template_url(self, app):
        pass

    def get_controller(self, app):
        return 'Html5'

    def angular_page(self, app, page):
        '''Callback for adding additional data to angular page object
        '''
        pass

    def sitemap(self, app, doc, uirouter):
        '''Build the sitemap used by angular `ui-router`_
        '''
        root = self.angular_root
        if root._sitemap is None:
            add_ng_modules(doc, ('ui.router',))
            sitemap = {'hrefs': [],
                       'pages': {},
                       'uiRouter': uirouter}
            add_to_sitemap(sitemap, app, doc, root)
            root._sitemap = sitemap
        return root._sitemap

    def childname(self, prefix):
        return '%s%s' % (self.name, prefix) if self.name else prefix

    def instance_url(self, request, instance):
        '''Return the url for editing the ``instance``
        '''
        pass

    def make_router(self, rule, method=None, handler=None, cls=None, **params):
        if not cls:
            cls = Router
        return super().make_router(rule, method=method, handler=handler,
                                   cls=cls, **params)


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


def add_to_sitemap(sitemap, app, doc, router, parent=None):
    # Router variables
    if not isinstance(router, Router):
        return
    uirouter = app.config['ANGULAR_UI_ROUTER'] and router.uirouter
    if (not uirouter or
            (parent and
             router.parent.html_body_template != router.html_body_template)):
        return

    # path for the current router
    path = router_href(app, router.full_route)
    #
    page = {'url': path,
            'name': router.name,
            'template': router.state_template(app),
            'templateUrl': router.state_template_url(app),
            'api': router.get_api_info(app),
            'controller': router.get_controller(app),
            'parent': parent}
    router.angular_page(app, page)
    sitemap['hrefs'].append(path)
    sitemap['pages'][path] = page
    add_ng_modules(doc, router.ngmodules)
    #
    # Loop over children routes
    for child in router.routes:
        #
        # This is the first child
        if not parent:
            getmany = True
            apiname = router.name
        add_to_sitemap(sitemap, app, doc, child, path)

    # Add redirect to folder page if required
    if path.endswith('/') and path != '/':
        rpath = path[:-1]
        if rpath not in sitemap['pages']:
            page = {'url': rpath,
                    'redirectTo': path}
            sitemap['hrefs'].append(rpath)
            sitemap['pages'][rpath] = page
