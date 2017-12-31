from collections import OrderedDict
from pulsar.api import Http404

from lux.core import JsonRouter
from lux.models import Model
from lux.openapi import METHODS


REST_CONTENT_TYPES = ['application/json']
CREATE_MODEL_ERROR_MSG = 'Could not create model'


class RestRoot(JsonRouter):
    '''Api Root

    Provide a get method for displaying a dictionary of api names - api urls
    key - value pairs
    '''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        for router in self.routes:
            url = '%s%s' % (request.absolute_uri('/'), router.route.rule)
            if isinstance(router, RestRouter) and router.model:
                routes[router.model.uri] = url
            else:
                routes[router.name] = url
        return routes

    def get(self, request):
        apis = self.apis(request)
        data = OrderedDict(((name, apis[name]) for name in sorted(apis)))
        return request.json_response(data)


class Rest404(JsonRouter):
    response_content_types = REST_CONTENT_TYPES

    def get(self, request):
        raise Http404


class RestRouter(JsonRouter):
    '''A mixin to be used in conjunction with Routers, usually
    as the first class in the multi-inheritance declaration
    '''
    response_content_types = REST_CONTENT_TYPES

    def __init__(self, *args, **kwargs):
        url = None
        if args:
            url_or_model, args = args[0], args[1:]
            if isinstance(url_or_model, Model):
                self.model = url_or_model
            else:
                url = url_or_model

        if not self.model:
            self.model = kwargs.pop('model', None)

        if self.model:
            if url is None:
                url = self.model.uri
            else:
                url = url.format(self.model.uri)

        rule_methods = {}
        for name, info in self.rule_methods.items():
            openapi = info.parameters.get('openapi')
            # don't consider new routes the standard methods,
            # they are already dealt with
            if openapi and name in METHODS:
                continue
            rule_methods[name] = info
        self.rule_methods = rule_methods
        super().__init__(url, *args, **kwargs)
