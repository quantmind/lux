from pulsar import Http404
from pulsar.utils.html import nicename

import lux
from lux import route
from lux.extensions import rest

# Override Default Admin Router for a model
adminMap = {}


class register:
    '''Register an admin router class for a model
    '''
    def __init__(self, name):
        self.name = name

    def __call__(self, cls):
        assert issubclass(cls, AdminModel)
        assert cls is not AdminModel
        adminMap[self.name] = cls


class AdminRouter(lux.HtmlRouter):

    def response_wrapper(self, callable, request):
        app = request.app
        permission = app.config['ADMIN_PERMISSIONS']
        if permission:
            backend = request.cache.auth_backend
            if backend.has_permission(request, permission, rest.READ):
                return callable(request)
            else:
                raise Http404
        else:
            return callable(request)

    def get(self, request):
        if request.url_data.get('template') == 'ui':
            template = self.get_html(request)
            request.response.content = template
            return request.response
        else:
            admin = self.admin_root()
            assert admin
            doc = request.html_document
            doc.jscontext['navigation'] = admin.sitemap(request.app)
            return super().get(request)

    def get_html(self, request):
        return request.app.render_template('partials/admin.html')

    def admin_root(self):
        router = self
        while router and not isinstance(router, Admin):
            router = router.parent
        return router

    def angular_page(self, app, router, page):
        '''Add angular router information (lux.extensions.angular)
        '''
        page['templateUrl'] = '%s?template=ui' % router.full_route


class Admin(AdminRouter):
    '''Admin Root'''
    _sitemap = None

    def __init__(self, *args, **kwargs):
        # set self as the angular root
        self._angular_root = self
        super().__init__(*args, **kwargs)

    def sitemap(self, app):
        if self._sitemap is None:
            sections = {}
            sitemap = []
            for child in self.routes:
                if isinstance(child, AdminModel):
                    section, info = child.info(app)

                    if section not in sections:
                        items = []
                        sections[section] = {'name': section,
                                             'items': items}
                        sitemap.append(sections[section])
                    else:
                        items = sections[section]['items']

                    items.append(info)

            self._sitemap = sitemap
        return self._sitemap


class AdminModel(AdminRouter):
    section = None
    icon = None

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__('/%s' % self.model, *args, **kwargs)

    def info(self, app):
        '''Information for admin navigation
        '''
        info = {'title': nicename(self.model),
                'name': nicename(self.model),
                'href': self.full_route.path,
                'icon': self.icon}
        return self.section, info

    def get_html(self, request):
        return request.app.render_template('partials/admin-list.html')

    @route
    def add(self, request):
        '''Add a new model
        '''
        raise Http404

    @route('<id>')
    def update(self, request):
        '''Add a new model'''
        raise Http404
