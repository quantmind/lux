from inspect import isclass

from pulsar import Http404, PermissionDenied
from pulsar.apps.wsgi import Json
from pulsar.utils.html import nicename

from lux.core import route, cached, HtmlRouter
from lux.forms import get_form_layout
from lux.extensions.angular import grid

# Override Default Admin Router for a model
adminMap = {}


def is_admin(cls, check_model=True):
    if isclass(cls) and issubclass(cls, AdminModel) and cls is not AdminModel:
        return bool(cls.model) if check_model else True
    return False


class register:
    '''Decorator to register an admin router class with
    REST model.

    :param model: a string or a :class:`~lux.extensions.rest.RestModel`
    '''
    def __init__(self, model):
        self.model = model

    def __call__(self, cls):
        assert is_admin(cls, False)
        cls.model = self.model
        adminMap[self.model] = cls
        return cls


class AdminRouter(HtmlRouter):
    '''Base class for all Admin Routers
    '''
    def response_wrapper(self, callable, request):
        backend = request.cache.auth_backend
        if backend.has_permission(request, 'site:admin', 'read'):
            return callable(request)
        else:
            raise Http404

    def context(self, request):
        '''Override to add the admin navigation to the javascript context.

        The navigation entry can be used to build the admin web pages
        '''
        admin = self.admin_root()
        if admin:
            doc = request.html_document
            doc.jscontext['navigation'] = admin.sitemap(request)

    def get_html(self, request):
        return request.app.render_template('partials/admin.html')

    def admin_root(self):
        router = self
        while router and not isinstance(router, Admin):
            router = router.parent
        return router


class Admin(AdminRouter):
    """Admin Root - contains all Admin routers managing models.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set self as the angular root
        self._angular_root = self

    @cached(user=True)
    def sitemap(self, request):
        infos = []
        resources = []
        for child in self.routes:
            if isinstance(child, AdminModel):
                resource = child.model
                resources.append(resource)
                section, info = child.info(request)
                infos.append((resource, section, info))

        backend = request.cache.auth_backend
        sections = {}
        sitemap = []

        if backend:
            permissions = backend.get_permissions(request, resources, 'read')
            infos = self._permission_filter(permissions, infos)

        for resource, section, info in infos:
            if section not in sections:
                items = []
                sections[section] = {'name': section,
                                     'items': items}
                sitemap.append(sections[section])
            else:
                items = sections[section]['items']

            items.append(info)

        return sitemap

    def _permission_filter(self, permissions, infos):
        for resource, section, info in infos:
            permission = permissions.get(resource)
            if permission and permission.get('read'):
                yield resource, section, info


class AdminModel(AdminRouter):
    '''Router for rendering an admin section relative to
    a given rest model
    '''
    model = None
    section = None
    permissions = None
    '''An permissions used in grid
    '''
    icon = None
    '''An icon for this Admin section
    '''
    def __init__(self):
        assert self.model
        super().__init__(self.model)

    def info(self, request):
        '''Information for admin navigation
        '''
        model = self.get_model(request)
        url = model.url
        name = nicename(url)
        info = {'title': name,
                'name': name,
                'href': self.full_route.path,
                'icon': self.icon}
        return self.section, info

    def get_html(self, request):
        app = request.app
        model = self.get_model(request)
        options = dict(target=model.get_target(request))
        if self.permissions is not None:
            options['permissions'] = self.permissions
        context = {'grid': grid(options)}
        return app.render_template('partials/admin-list.html', context)


class CRUDAdmin(AdminModel):
    '''An Admin model Router for adding and updating models
    '''
    form = None
    updateform = None
    addtemplate = 'partials/admin-add.html'

    @route()
    def add(self, request):
        '''Add a new model
        '''
        return self.get_form(request, self.form)

    @route('<id>')
    def update(self, request):
        '''Edit an existing model
        '''
        id = request.urlargs['id']
        form = self.updateform or self.form
        return self.get_form(request, form, id=id)

    def get_form(self, request, form=None, id=None):
        json = 'json' in request.url_data
        if id:
            action = 'update'
            form = form or self.updateform or self.form
        else:
            action = 'create'
            form = form or self.form

        form = get_form_layout(request, form)
        if not form:
            raise Http404

        backend = request.cache.auth_backend
        model = self.get_model(request)
        target = model.get_target(request, path=id, action=action)
        if id:
            request.api.head(target)

        if backend.has_permission(request, model.name, action):
            if json:
                data = form(request).as_dict(action=target)
                return Json(data).http_response(request)
            else:
                html = form(request).as_form(action=target)
                context = {'html_form': html.render()}
                html = request.app.render_template(self.addtemplate, context)
                return self.html_response(request, html)

        raise PermissionDenied
