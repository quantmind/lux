'''
HTML5 Router and utilities.
'''
import lux

from pulsar import Http404
from pulsar.apps.wsgi import MediaMixin, route


class Router(lux.Router, MediaMixin):
    '''A :class:`.Router` for Html5 navigation
    '''
    in_nav = True
    target = None
    title = None
    has_content = True
    html_body_template = 'home.html'
    '''The template for the body part of the Html5 document
    '''
    _sitemap = None

    def get(self, request):
        '''The get view'''
        app = request.app
        doc = request.html_document
        doc.attr({'ng-model': 'page',
                  'ng-controller': 'page'})
        jscontext = self.sitemap(app).copy()
        jscontext['page'] = router_href(request.app_handler)
        return app.html_response(request, self.html_body_template,
                                 jscontext=jscontext)

    #@route('/partial/<path:path>')
    def partial_template(self, request):
        '''Default route to serve partial templates.

        To override this view in a child router, create a
        route with ``name`` equal to ``partial_template``.
        '''
        name = request.urlargs['path']
        template_path = request.app.template_full_path(name)
        if template_path:
            return self.serve_file(request, template_path)
        else:
            raise Http404

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

    def html_response(self, request, ctx):
        '''Build the html response
        '''
        app = request.app
        ctx = self.sitemap(app)
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
            'api': router.get_api_name(),
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
