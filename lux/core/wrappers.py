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
from pulsar import get_event_loop
from pulsar.apps.wsgi import (route, wsgi_request, cached_property,
                              EnvironMixin, html_factory)
from pulsar.apps import wsgi
from pulsar.apps.wsgi import RouterParam
from pulsar.utils.httpurl import JSON_CONTENT_TYPES
from pulsar.utils.structures import mapping_iterator

from lux.utils import unique_tuple

__all__ = ['Html', 'HtmlRouter',
           'WsgiRequest', 'Router', 'route', 'wsgi_request', 'as_tag',
           'cached_property', 'EnvironMixin', 'html_factory',
           'get_event_loop', 'RouterParam', 'JSON_CONTENT_TYPES',
           'DEFAULT_CONTENT_TYPES']

Html = wsgi.Html

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
    '''Extend :class:`~pulsar.apps.wsgi.WsgiRequest` with additional
    methods and attributes.
    '''
    @property
    def app(self):
        '''The :class:`.App` running the website.'''
        return self.cache.app

    @property
    def config(self):
        '''The configuration dictionary'''
        return self.cache.app.config

    @property
    def logger(self):
        '''Shortcut to app logger'''
        return self.cache.app.logger

    @property
    def models(self):
        '''The router to registered models for the application serving
        the request'''
        return self.cache.app.local.models

    @cached_property
    def html_document(self):
        '''The HTML document for this request.'''
        return self.app.html_document(self)

    @cached_property
    def cache_server(self):
        cache = self.config['CACHE_SERVER']
        if isinstance(cache, str):
            raise NotImplementedError
        return cache

    def has_permission(self, action, model):
        '''Check if this request has permission on ``model`` to perform a
        given ``action``'''
        return self.app.permissions.has(self, action, model)


wsgi.set_wsgi_request_class(WsgiRequest)


class Router(wsgi.Router):
    '''Extend pulsar :class:`~pulsar.apps.wsgi.routers.Router` with content
    management.'''
    in_nav = False
    content_manager = None
    controller = None
    form = RouterParam(None)

    def __init__(self, *args, **kwargs):
        super(Router, self).__init__(*args, **kwargs)
        if self.content_manager:
            self.content_manager = self.content_manager._clone(self)

    def get_controller(self):
        if self.controller:
            return self.controller
        elif self.form:
            return self.form.layout.controller

    def template_response(self, request, template):
        '''A text/html response with an angular template
        '''
        response = request.response
        response.content_type = 'text/plain'
        response.content = template
        return response

    def make_router(self, rule, cls=None, **params):
        '''Create a new :class:`.Router` form rule and parameters
        '''
        cls = cls or Router
        return cls(rule, **params)

    def add_api_urls(self, request, api):
        for r in self.routes:
            if isinstance(r, Router):
                r.add_api_urls(request, api)

    def get_api_info(self, app):
        '''The api name for this :class:`.Router`
        '''


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


class HeadMeta(object):
    '''Wrapper for HTML5 head metatags.
    '''
    def __init__(self, head):
        self.head = head

    def __repr__(self):
        return repr(self.head.meta.children)

    def __str__(self):
        return str(self.head.meta.children)

    def update(self, iterable):
        for name, value in mapping_iterator(iterable):
            self.set(name, value)

    def __setitem__(self, entry, content):
        self.set(entry, content)

    def __getitem__(self, entry):
        return self.get(entry)

    def __len__(self):
        return len(self.head.meta.children)

    def __iter__(self):
        return iter(self.head.meta.children)

    def set(self, entry, content, meta_key=None):
        '''Set the a meta tag with ``content`` and ``entry`` in the HTML5 head.
        The ``key`` for ``entry`` is either ``name`` or ``property`` depending
        on the value of ``entry``.
        '''
        if content:
            if entry == 'title':
                self.head.title = content
            else:
                self.head.replace_meta(entry, content, meta_key)

    def get(self, entry, meta_key=None):
        if entry == 'title':
            return self.head.title
        else:
            return self.head.get_meta(entry, meta_key=meta_key)
