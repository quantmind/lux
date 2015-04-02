from pulsar import Http404
from pulsar.utils.html import nicename

import lux
from lux import route

# Override Default Admin Router for a model
adminMap = {}


class register:
    '''Register an admin router class for a model
    '''
    def __init__(self, name):
        self.name

    def __call__(self, cls=None, form=None):
        if not cls:
            name = 'AdminModel%s' % self.name
            cls = type(AdminModel)(name, (AdminModel,), {})
        assert issubclass(cls, AdminModel)
        assert cls is not AdminModel
        if form:
            cls.form = form
        adminMap[self.name] = cls


class AdminRouter(lux.HtmlRouter):

    def get_html(self, request):
        doc = request.html_document
        nav = {'top': True,
               'items2': self.sitemap(request)}
        doc.jscontext['adminNavigation'] = nav
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

    def __init__(self, meta, *args, **kwargs):
        self.meta = meta
        super().__init__('/%s/' % meta.name, *args, **kwargs)

    def info(self, app):
        info = app.mapper.api_info(self.meta)
        if info:
            info['label'] = nicename(info['name'])
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
