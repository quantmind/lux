from inspect import isclass

from pulsar import Http404, PermissionDenied
from pulsar.apps.wsgi.routers import RouterType
from pulsar.utils.html import nicename

import lux
from lux import route, cached
from lux.extensions import rest
from lux.extensions.angular import grid

# Override Default Admin Router for a model
adminMap = {}


def is_admin(cls, check_model=True):
    if isclass(cls) and issubclass(cls, AdminModel) and cls is not AdminModel:
        return bool(cls._model) if check_model else True
    return False


class register:
    '''Decorator to register an admin router class with
    REST model.

    :param model: a string or a :class:`~lux.extensions.rest.RestModel`
    '''
    def __init__(self, model):
        if isinstance(model, RouterType):
            model = model._model
        if not isinstance(model, rest.RestModel):
            model = rest.RestModel(model)
        self.model = model

    def __call__(self, cls):
        assert is_admin(cls, False)
        cls._model = self.model
        adminMap[self.model.name] = cls
        return cls


class AdminRouter(lux.HtmlRouter):
    '''Base class for all Admin Routers
    '''
    def response_wrapper(self, callable, request):
        backend = request.cache.auth_backend
        if backend.has_permission(request, 'site:admin', 'READ'):
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
    '''Admin Root

    This router containes all Admin routers managing models.
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set self as the angular root
        self._angular_root = self

    @cached
    def sitemap(self, request):
        sections = {}
        sitemap = []
        for child in self.routes:
            if isinstance(child, AdminModel):
                section, info = child.info(request)

                if section not in sections:
                    items = []
                    sections[section] = {'name': section,
                                         'items': items}
                    sitemap.append(sections[section])
                else:
                    items = sections[section]['items']

                items.append(info)

        return sitemap


class AdminModel(rest.RestMixin, AdminRouter):
    '''Router for rendering an admin section relative to
    a given rest model
    '''
    section = None
    permissions = None
    '''An permissions used in grid
    '''
    icon = None
    '''An icon for this Admin section
    '''
    uimodules = ('lux.grid',)

    def info(self, request):
        '''Information for admin navigation
        '''
        model = self._model
        name = nicename(model.name)
        info = {'title': name,
                'name': name,
                'href': self.full_route.path,
                'icon': self.icon}
        return self.section, info

    def get_html(self, request):
        app = request.app
        model = self._model
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

    def get_form(self, request, form, id=None):
        if not form:
            raise Http404
        action = 'update' if id else 'create'
        backend = request.cache.auth_backend
        model = self._model

        if backend.has_permission(request, model.name, action):
            target = model.get_target(request, path=id, get=True)
            html = form(request).as_form(action=target, actionType=action)
            context = {'html_form': html.render()}
            html = request.app.render_template(self.addtemplate, context)
            return self.html_response(request, html)
        raise PermissionDenied
