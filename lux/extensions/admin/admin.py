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

    def get_html(self, request):
        doc = request.html_document
        return request.app.template('partials/admin.html')

    def sitemap(self, request):
        router = request.app_handler
        while not isinstance(router, Admin):
            router = router.parent
        if router:
            sitemap = []
            for child in router.routes:
                if isinstance(child, AdminModel):
                    info = child.info(request.app)
                    if info:
                        sitemap.append(info)
        return sitemap


class Admin(AdminRouter):
    '''Admin Root'''


class AdminModel(AdminRouter):

    def __init__(self, model, *args, **kwargs):
        self.model = model
        super().__init__('/%s' % self.model, *args, **kwargs)

    def info(self, app):
        info = {}
        info['label'] = nicename(self.model)
        info['href'] = self.full_route.path
        return info

    @route
    def add(self, request):
        '''Add a new model'''
        raise Http404

    @route('<id>')
    def read(self, request):
        '''Add a new model'''
        raise Http404

    @route('<id>')
    def update(self, request):
        '''Add a new model'''
        raise Http404
