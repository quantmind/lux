'''
.. _router:

Router
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: Router
   :members:
   :member-order: bysource


.. _htmlrouter:

Html Router
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: HtmlRouter
   :members:
   :member-order: bysource

Wsgi Request
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: WsgiRequest
   :members:
   :member-order: bysource
'''
from functools import wraps

from pulsar import (HttpException, ContentNotAccepted, Http404, get_event_loop,
                    multi_async)
from pulsar.utils.system import json
from pulsar.utils.structures import AttributeDictionary
from pulsar.apps.wsgi import (route, wsgi_request, cached_property,
                              EnvironMixin, html_factory)
from pulsar.apps import wsgi
from pulsar.apps.wsgi import RouterParam
from pulsar.utils.httpurl import JSON_CONTENT_TYPES

from lux.utils import unique_tuple

__all__ = ['Html', 'HtmlRouter', 'headers',
           'WsgiRequest', 'Router', 'route', 'wsgi_request', 'as_tag',
           'cached_property', 'EnvironMixin', 'html_factory',
           'get_event_loop', 'RouterParam', 'JSON_CONTENT_TYPES',
           'DEFAULT_CONTENT_TYPES']


def frozen_set(*elems):
    def _():
        for elem in elems:
            if isinstance(elem, str):
                yield elem
            else:
                for el in elem:
                    yield el
    return frozenset(_())


def as_tag(elem, tag):
    if not isinstance(elem, wsgi.Html) or elem.tag != tag:
        return Html(tag, elem)
    return elem


DEFAULT_CONTENT_TYPES = unique_tuple(('text/html', 'text/plain', 'text/csv'),
                                     JSON_CONTENT_TYPES)


class WsgiRequest(wsgi.WsgiRequest):
    '''Extend pulsar Wsgi Request with additional methods and attributes.'''
    @property
    def app(self):
        '''The :class:`lux.core.App` running the website.'''
        return self.cache.app

    @property
    def models(self):
        '''The router to registered models for the application serving
        the request'''
        return self.cache.app.local.models

    @cached_property
    def html_document(self):
        '''The HTML document for this request.'''
        return self.app.html_document(self)

    def has_permission(self, action, model):
        '''Check if this request has permission on ``model`` to perform a
        given ``action``'''
        return self.app.permissions.has(self, action, model)


wsgi.set_wsgi_request_class(WsgiRequest)


class headers:

    def __init__(self, content_type=None, cache=None):
        self.content_type = content_type
        self.cache = cache

    def __call__(self, method):

        @wraps(method)
        def _(router, request):
            response = request.response
            if self.content_type:
                if (response.content_type is None and
                        not request.get('HTTP_ACCEPT')):
                    response.content_type = self.content_type
                elif response.content_type != self.content_type:
                    raise ContentNotAccepted()
            if self.cache:
                self.cache(response.headers)
            return method(router, request)

        return _


class Router(wsgi.Router):
    '''Extend pulsar Router with content management.'''
    content_manager = None
    '''Optional :class:`lux.core.content.ContentManager`.

    A content manager can be used to separate the matching and parsing
    of a URL, provided by the :class:`Router` with the actual handling of
    the request.'''

    def __init__(self, *args, **kwargs):
        super(Router, self).__init__(*args, **kwargs)
        if self.content_manager:
            self.content_manager = self.content_manager._clone(self)

    def html_url(request, item):
        '''Return an :ref:`Html Link <html-link>` object for ``item``.'''
        pass


class HtmlRouter(Router):
    '''A pulsar Router for html content.

It introduces the following:

.. attribute:: in_sitemap

    Boolean indicating if the route served by the Router can be included in
    the site-map.
    '''
    response_content_types = RouterParam(DEFAULT_CONTENT_TYPES)
    in_sitemap = RouterParam(True)
    icon = None


class Html(wsgi.Html):

    def http_response(self, request):
        doc = request.html_document
        if doc.is_html:
            # if the content type is text/html fire the on_html_response event
            html = {'body': self}
            request.app.fire('on_html_response', request, html)
            inner = html['body']
            doc.body.append(html['body'])
        return doc.http_response(request)


class JsonDocument(wsgi.HtmlDocument):

    @property
    def is_html(self):
        return False

    def do_stream(self, request):
        yield self.to_json(request)

    def to_json(self):
        self.body._tag = None
        body = yield multi_async(self.body.stream(request))
        self.head._tag = None
        data = {'body': body}
        data.extend(self.head.to_json())
        coroutine_return(json.dumps(data))
