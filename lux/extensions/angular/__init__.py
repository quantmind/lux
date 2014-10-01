'''
HTML5 Router and utilities
'''
import lux
from lux import Parameter

from pulsar import Http404
from pulsar.apps.wsgi import MediaMixin, Html, route

from .ui import add_css


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('HTML5_NAVIGATION', False, 'Enable Html5 navigation'),
        Parameter('NAVBAR_COLLAPSE_WIDTH', 768,
                  'Width when to collapse the navbar'),
        Parameter('NGMODULES', [], 'Angular module to load')
    ]

    def jscontext(self, request, context):
        width = request.config['NAVBAR_COLLAPSE_WIDTH']
        context['navbarCollapseWidth'] = width


class Router(lux.Router, MediaMixin):
    '''A :class:`.Router` for Angular Html5 navigation

    When the :setting:`HTML5_NAVIGATION` is ``True``, this router
    does not build the ``$main`` key for the context dictionary, insteady
    it places the

        <div ng-view></div>

    tag and populate the javascript context dictionary with a sitemap
    and the ``html5mode`` flag set to ``True``.
    '''
    in_nav = True
    target = None
    title = None
    api = None
    has_content = True
    angular_view_class = 'angular-view'
    html_body_template = 'home.html'
    '''The template for the body part of the Html5 document
    '''
    ngmodules = None
    '''List of angular modules to include
    '''
    _sitemap = None

    def get(self, request):
        app = request.app
        html5 = app.config['HTML5_NAVIGATION']
        doc = request.html_document
        doc.body.data({'ng-model': 'page',
                       'ng-controller': 'Page'})
        jscontext = {}
        context = {}
        #
        # Using Angular Ui-Router
        if html5:
            jscontext.update(self.sitemap(app))
            jscontext['page'] = router_href(request.app_handler.full_route)
        else:
            ngmodules = set(app.config['NGMODULES'])
            if self.ngmodules:
                ngmodules.update(self.ngmodules)
            jscontext['ngModules'] = tuple(ngmodules)

        main = self.build_main(request, context, jscontext)
        if html5:
            main = self.uiview(app, main)

        context['html_main'] = main
        return app.html_response(request, self.html_body_template,
                                 jscontext=jscontext, context=context)

    def build_main(self, request, context, jscontext):
        '''Build the context when not using html5 navigation
        '''
        return {}

    def uiview(self, app, main):
        div = Html('div', main, cn=self.angular_view_class)
        div.data('ui-view', '')
        return div.render()

    def state_template(self, app):
        '''Template for ui-router state associated with this router'''
        pass

    def get_controller(self, app):
        return 'Html5'

    def angular_page(self, app, page):
        '''Callback for adding additional data to angular page object
        '''
        pass

    def sitemap(self, app):
        '''Build the sitemap used by angular ui-router
        '''
        root = self.root
        if root._sitemap is None:
            ngmodues = set(app.config['NGMODULES'])
            ngmodues.add('ui.router')
            sitemap = {'hrefs': [],
                       'pages': {},
                       'html5mode': True,
                       'ngModules': ngmodues}
            add_to_sitemap(sitemap, app, root)
            sitemap['ngModules'] = tuple(ngmodues)
            root._sitemap = sitemap
        return root._sitemap

    def childname(self, prefix):
        return '%s%s' % (self.name, prefix) if self.name else prefix

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


def router_href(route):
    url = '/'.join(_angular_route(route))
    if url:
        return '/%s' % url if route.is_leaf else '/%s/' % url
    else:
        return '/'


def _angular_route(route):
    for is_dynamic, val in route.breadcrumbs:
        if is_dynamic:
            c = route._converters[val]
            yield '*%s' % val if c.regex == '.*' else ':%s' % val
        else:
            yield val


def add_to_sitemap(sitemap, app, router, parent=None):
    '''Add router and its children to the Html5 sitemap
    '''
    # Router variables
    if not isinstance(router, Router):
        return
    href = router_href(router.full_route)
    #site_url = app.config['SITE_URL']
    #if site_url:
    #    href = site_url + href if href != '/' else site_url
    #
    # Target
    target = router.target
    if not target and router.parent:
        if router.parent.html_body_template != router.html_body_template:
            target = '_self'
    #
    page = {'url': href,
            'name': router.name,
            'target': target,
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
        # In navigation
        if getattr(router, 'in_nav', False):
            add_to_sitemap(sitemap, app, child, href)
