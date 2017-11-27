from pulsar.api import Http404
from pulsar.apps.wsgi import RouterParam, Router, Route, route
from pulsar.utils.httpurl import JSON_CONTENT_TYPES, CacheControl

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
    """Extend pulsar Router
    with content management.
    """
    response_content_types = DEFAULT_CONTENT_TYPES

    def check_permission(self, request):
        resource = Resource.app(request)
        resource(request)

    def get(self, request):
        html = self.get_html(request)
        return request.app.cms.html_response(request, html)

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
        schema = self.schema
        # schema = schema2jsonschema(self.schema)
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


def raise404(request):
    raise Http404
