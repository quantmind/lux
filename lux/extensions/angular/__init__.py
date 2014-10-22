'''\
THis extension does not provide any middleware but it is required
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
from lux import Parameter

from pulsar.apps.wsgi import MediaMixin, Html, route
from pulsar.utils.httpurl import urlparse

from .ui import add_css


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


class Router(lux.Router, MediaMixin):
    '''A :class:`.Router` for Angular navigation.
    '''
    in_nav = True
    title = None
    api = None
    has_content = True
    angular_view_class = 'angular-view'
    html_body_template = 'home.html'
    '''The template for the body part of the Html5 document. In most cases it
    is as simple as::

        $html_main

    where the ``$html_main`` is replaced by the string created by the
    :meth:`build_main` method.
    '''
    ngmodules = None
    '''Optional list of angular modules to include
    '''
    uirouter = True
    '''Override the :setting:`ANGULAR_UI_ROUTER` setting for this
    :class:`.Router`. If set to ``False`` the `ui-router`_ won't be used
    and the whole html5 document is loaded when accessed.'''
    _sitemap = None

    def get(self, request):
        '''This is the only http method implemented.

        If this :class:`.Router` is operating in :ref:`ui mode <spa-router>`,
        this method performs the following tasks:

        * Collets children routers operating in :ref:`ui mode <spa-router>`
          and build the sitemap used by angular `ui-router`_.
        * The ``$html_main`` content, rendered by the :meth:`build_main` method is
          wrapped by a ``div`` element::

            <div id="seo-view" data-ui-main="main" class="hidden">
                $html_main
            </div>
        '''
        app = request.app
        uirouter = app.config['ANGULAR_UI_ROUTER'] and self.uirouter
        doc = request.html_document
        doc.body.data({'ng-model': 'page',
                       'ng-controller': 'Page',
                       'page': ''})
        #
        # Add info to jscontext
        jscontext = doc.jscontext
        jscontext['html5mode'] = app.config['HTML5_NAVIGATION']
        navbar = doc.jscontext.get('navbar') or {}
        navbar['collapseWidth'] = app.config['NAVBAR_COLLAPSE_WIDTH']
        jscontext['navbar'] = navbar
        #
        # Build the ui-view main
        main = self.build_main(request)
        #
        ngmodules = jscontext['ngModules'] = set(jscontext.get('ngModules', ()))
        ngmodules.update(app.config['NGMODULES'])
        #
        # Using Angular Ui-Router
        if uirouter:
            jscontext.update(self.sitemap(app, ngmodules))
            jscontext['page'] = router_href(app,
                                            request.app_handler.full_route)
        elif self.ngmodules:
            ngmodules.update(self.ngmodules)

        if uirouter:
            main = self.uiview(app, main, jscontext)

        jscontext['ngModules'] = list(jscontext['ngModules'])
        context = {'html_main': main}
        return app.html_response(request, self.html_body_template,
                                 context=context)

    def build_main(self, request):
        '''Build the main view for this router
        '''
        return ''

    def uiview(self, app, main, jscontext):
        '''Wrap the ``main`` html with a ``ui-view`` container.
        Add animation class if specified in :setting:`ANGULAR_VIEW_ANIMATE`.
        '''
        main = Html('div', main, cn='hidden', id="seo-view")
        div = Html('div', main, cn=self.angular_view_class)
        animate = app.config['ANGULAR_VIEW_ANIMATE']
        if animate:
            jscontext['ngModules'].add('ngAnimate')
            div.addClass(animate)
        div.data('ui-view', 'main')
        return div.render()

    def state_template(self, app):
        '''Template for ui-router state associated with this router.
        '''
        pass

    def get_controller(self, app):
        return 'Html5'

    def angular_page(self, app, page):
        '''Callback for adding additional data to angular page object
        '''
        pass

    def sitemap(self, app, ngmodules):
        '''Build the sitemap used by angular `ui-router`_
        '''
        root = self.root
        if root._sitemap is None:
            ngmodules.add('ui.router')
            sitemap = {'hrefs': [],
                       'pages': {},
                       'uiRouter': True,
                       'ngModules': ngmodules}
            add_to_sitemap(sitemap, app, root)
            root._sitemap = sitemap
        return root._sitemap

    def childname(self, prefix):
        return '%s%s' % (self.name, prefix) if self.name else prefix

    def instance_url(self, request, instance):
        '''Return the url for editing the ``instance``
        '''
        pass

    def make_router(self, rule, method=None, handler=None, cls=None, **params):
        cls = cls or Router
        if cls is Router and method == 'get':
            method = 'build_main'
        return super(Router, self).make_router(rule, method=method, handler=handler, cls=cls, **params)


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


def add_to_sitemap(sitemap, app, router, parent=None):
    # Router variables
    if not isinstance(router, Router):
        return
    uirouter = app.config['ANGULAR_UI_ROUTER'] and router.uirouter
    if (not uirouter or 
            (router.parent and
             router.parent.html_body_template != router.html_body_template)):
        return
    
    href = router_href(app, router.full_route)
    #
    page = {'url': href,
            'name': router.name,
            'template': router.state_template(app),
            'api': router.get_api_info(app),
            'controller': router.get_controller(app),
            'parent': parent}
    router.angular_page(app, page)
    sitemap['hrefs'].append(href)
    sitemap['pages'][href] = page
    if router.ngmodules:
        sitemap['ngModules'].update(router.ngmodules)
    #
    # Loop over children routes
    for child in router.routes:
        #
        # This is the first child
        if not parent:
            getmany = True
            apiname = router.name
        add_to_sitemap(sitemap, app, child, href)
