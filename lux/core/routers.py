from pulsar.api import Http404
from pulsar.apps.wsgi import RouterParam, Router, Route, Html, route
from pulsar.utils.httpurl import JSON_CONTENT_TYPES, CacheControl

from apispec.ext.marshmallow.swagger import schema2jsonschema

from ..utils.data import unique_tuple
from .auth import Resource
from ..utils.data import compact_dict


DEFAULT_CONTENT_TYPES = unique_tuple(('text/html', 'text/plain', 'text/csv'),
                                     JSON_CONTENT_TYPES)


class RedirectRouter(Router):

    def __init__(self, routefrom, routeto):
        super().__init__(routefrom, routeto=Route(routeto))

    def get(self, request):
        url = self.routeto.url(**request.urlargs)
        return request.redirect(url)


class JsonRouter(Router):
    model = RouterParam()
    cache_control = CacheControl()
    response_content_types = ['application/json']

    def head(self, request):
        if hasattr(self, 'get'):
            return self.get(request)

    def json_response(self, request, data):
        """Return a response as application/json
        """
        return self.cache_control(request.json_response(data))

    def get_model(self, request, model=None):
        model = request.app.models.get(model or self.model)
        if not model:
            raise Http404
        return model


class HtmlRouter(JsonRouter):
    """Extend pulsar :class:`~pulsar.apps.wsgi.routers.Router`
    with content management.
    """
    response_content_types = DEFAULT_CONTENT_TYPES

    def check_permission(self, request):
        resource = Resource.app(request)
        resource(request)

    def get(self, request):
        return self.html_response(request, self.get_html(request))

    def html_response(self, request, inner_html):
        app = request.app
        # get cms for this router
        cms = app.cms
        # fetch the cms page
        page = cms.page(request)
        # render the inner part of the html page
        if isinstance(inner_html, Html):
            inner_html = inner_html.to_string(request)
        page.inner_template = cms.inner_html(request, page, inner_html)

        # This request is for the inner template only
        if request.url_data.get('template') == 'ui':
            request.response.content = page.render_inner(request)
            response = request.response
        else:

            response = app.html_response(request, page, self.context(request))

        self.cache_control(response)
        return response

    def get_inner_template(self, request, inner_template=None):
        return inner_template or self.template

    def get_html(self, request):
        """Must be implemented by subclasses.

        This method should return the main part of the html body.
        It is rendered where the html_main key is placed.
        """
        return ''

    def context(self, request):
        """Add router specific entries to the template ``context`` dictionary
        """
        pass

    def childname(self, prefix):
        """key for a child router
        """
        return '%s%s' % (self.name, prefix) if self.name else prefix

    def make_router(self, rule, **params):
        """Create a new :class:`.Router` form rule and parameters
        """
        params.setdefault('cls', HtmlRouter)
        return super().make_router(rule, **params)

    def add_api_urls(self, request, api):
        for r in self.routes:
            if isinstance(r, Router):
                r.add_api_urls(request, api)

    def angular_page(self, app, router, page):
        """Add angular router information (lux.extensions.angular)
        """
        url = page['url']
        if router.route.variables:
            # Variables in the url
            # params = dict(((v, v) for v in router.route.variables))
            # url = router.route.url(**params)
            # A page with variable requires to be resolved by the api
            # The resolve requires a model
            page['resolveTemplate'] = True
        else:
            url = page['url']
        page['templateUrl'] = '%s?template=ui' % url


class WebFormRouter(HtmlRouter):
    """A Router for rending web forms
    """
    schema = None
    form_method = None
    form_enctype = 'multipart/form-data'
    form_action = None
    response_content_types = ['text/html',
                              'application/json']

    def get_html(self, request):
        if not self.schema:
            raise Http404
        tag = request.config['HTML_FORM_TAG']
        action = '%s/jsonform' % request.absolute_uri()
        return '<%s url="%s"></%s>' % (tag, action, tag)

    @route()
    def jsonform(self, request):
        if not self.schema:
            raise Http404
        schema = schema2jsonschema(self.schema)
        form = schema.get('properties')
        for name in schema.get('required', ()):
            form[name]['required'] = True
        method = self.form_method or 'post'
        action = self.form_action
        if hasattr(action, '__call__'):
            action = action(request)
        if not action:
            action = request.full_path()[:-9]
        data = compact_dict(action=action,
                            enctype=self.form_enctype,
                            method=method,
                            fields=form)
        return request.json_response(data)
