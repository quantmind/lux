'''
HTML5 Router and utilities
'''
import lux
from lux import Parameter

from pulsar import Http404
from pulsar.apps.wsgi import MediaMixin, route

from .ui import add_css


class Extension(lux.Extension):
    '''The sessions extensions provides wsgi middleware for managing sessions
    and users.

    In addition it provides utilities for managing Cross Site Request Forgery
    protection and user permissions levels.
    '''
    _config = [
        Parameter('HTML5_NAVIGATION', True, 'Enable Html5 navigation'),
        Parameter('NAVBAR_COLLAPSE_WIDTH', 768,
                  'Width when to collapse the navbar')
    ]

    def jscontext(self, request, context):
        width = request.config['NAVBAR_COLLAPSE_WIDTH']
        context['navbarCollapseWidth'] = width


class Router(lux.Router, MediaMixin):
    '''A :class:`.Router` for Html5 navigation

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
    template = None
    html_body_template = 'home.html'
    '''The template for the body part of the Html5 document
    '''
    _sitemap = None

    def get(self, request):
        app = request.app
        html5 = app.config.get('HTML5_NAVIGATION')
        doc = request.html_document
        doc.attr({'ng-model': 'page',
                  'ng-controller': 'page'})
        jscontext = {}
        context = {}
        main = self.build_main(request, context, jscontext)
        if html5:
            jscontext.update(self.sitemap(app))
            jscontext['page'] = router_href(request.app_handler)
            jscontext['html5mode'] = True
            main = '<div ng-view></div>'
        context['main'] = main
        return app.html_response(request, self.html_body_template,
                                 jscontext=jscontext, context=context)

    def build_main(self, request, context, jscontext):
        '''Build the context when not using html5 navigation
        '''
        return {}

    def html_title(self, app):
        return app.config['HTML_HEAD_TITLE']

    def sitemap(self, app):
        '''Build the sitemap for this router.
        '''
        root = self.root
        if root._sitemap is None:
            sitemap = {'hrefs': [], 'pages': {}, 'html5mode': True}
            add_to_sitemap(sitemap, app, root)
            root._sitemap = sitemap
        return root._sitemap

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


def router_href(router):
    vars = router.route.ordered_variables or None
    if vars:
        params = dict(((v, ':%s' % v) for v in vars))
        return router.path(**params)
    else:
        return router.path()


def add_to_sitemap(sitemap, app, router, parent=None):
    '''Add router and its children to the Html5 sitemap
    '''
    # Router variables
    if not isinstance(router, Router):
        return
    vars = router.route.ordered_variables or None
    href = router_href(router)
    #
    # Target
    target = router.target
    if not target and router.parent:
        if router.parent.html_body_template != router.html_body_template:
            target = '_self'
    #
    page = {'href': href,
            'vars': vars,
            'name': router.name,
            'target': target,
            'head_title': router.html_title(app),
            'title': router.title or router.name,
            'template': router.template,
            'api': router.get_api_info(app),
            'parent': parent}
    sitemap['hrefs'].append(href)
    sitemap['pages'][href] = page
    #
    controller = None
    partial_template = router.get_route('partial_template')
    if partial_template:
        controller = partial_template.get_controller()
        href = router_href(partial_template)
        vars = partial_template.route.ordered_variables or None
        page.update({'template_url': href,
                     'template_url_vars': vars})
    page['controller'] = controller or router.get_controller() or 'html5Page'
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
