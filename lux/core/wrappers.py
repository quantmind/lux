import json

from pulsar import ImproperlyConfigured
from pulsar.apps.wsgi import (route, wsgi_request, cached_property,
                              html_factory)
from pulsar.apps import wsgi
from pulsar.apps.wsgi import RouterParam, Router, render_error_debug
from pulsar.apps.wsgi.utils import error_messages
from pulsar.utils.httpurl import JSON_CONTENT_TYPES
from pulsar.utils.structures import mapping_iterator

from lux.utils import unique_tuple

__all__ = ['Html', 'WsgiRequest', 'Router', 'HtmlRouter',
           'JsonRouter', 'route', 'wsgi_request',
           'cached_property', 'html_factory', 'RedirectRouter',
           'RouterParam', 'JSON_CONTENT_TYPES',
           'DEFAULT_CONTENT_TYPES']

Html = wsgi.Html


TEXT_CONTENT_TYPES = unique_tuple(('text/html', 'text/plain'))

DEFAULT_CONTENT_TYPES = unique_tuple(('text/html', 'text/plain', 'text/csv'),
                                     JSON_CONTENT_TYPES)


class WsgiRequest(wsgi.WsgiRequest):
    '''Extend pulsar :class:`~pulsar.apps.wsgi.wrappers.WsgiRequest` with
    additional methods and attributes.
    '''
    @property
    def app(self):
        '''The :class:`.Application` running the website.'''
        return self.cache.app

    @property
    def config(self):
        '''The :attr:`.Application.config` dictionary'''
        return self.cache.app.config

    @property
    def logger(self):
        '''Shortcut to app logger'''
        return self.cache.app.logger

    @property
    def cache_server(self):
        return self.cache.app.cache_server

    @cached_property
    def html_document(self):
        '''The HTML document for this request.'''
        return self.app.html_document(self)

    @property
    def scheme(self):
        '''Protocol scheme, one of ``http`` and ``https``
        '''
        HEADER = self.config['SECURE_PROXY_SSL_HEADER']
        if HEADER:
            try:
                header, value = HEADER
            except ValueError:
                raise ImproperlyConfigured(
                    'The SECURE_PROXY_SSL_HEADER setting must be a tuple '
                    'containing two values.')
            return 'https' if self.environ.get(header) == value else 'http'
        return self.environ.get('HTTPS') == 'on'

    @property
    def is_secure(self):
        '''``True`` if this request is via a TLS connection
        '''
        return self.scheme == 'https'


wsgi.set_wsgi_request_class(WsgiRequest)


class RedirectRouter(Router):

    def __init__(self, routefrom, routeto):
        super(RedirectRouter, self).__init__(routefrom, routeto=routeto)

    def get(self, request):
        return request.redirect(self.routeto)


class JsonRouter(Router):
    response_content_types = ['application/json']


class HtmlRouter(Router):
    '''Extend pulsar :class:`~pulsar.apps.wsgi.routers.Router`
    with content management.
    '''
    in_nav = False
    html_body_template = None
    form = None
    uirouter = None
    uimodules = None
    model = None
    response_content_types = TEXT_CONTENT_TYPES

    def get(self, request):
        html = self.get_html(request)
        return self.html_response(request, html)

    def html_response(self, request, html):
        '''Render `html` as a full Html document or a partial.
        '''
        if isinstance(html, Html):
            html = html.render(request)

        # This request is for the inner template only
        if request.url_data.get('template') == 'ui':
            request.response.content = html
            return request.response

        context = {'html_main': html}
        self.context(request, context)
        app = request.app
        template = self.get_html_body_template(app)
        return app.html_response(request, template, context=context)

    def get_html(self, request):
        '''Must be implemented by subclasses.

        This method should return the main part of the html body.
        It is rendered where the $html_main key is placed.
        '''
        return ''

    def context(self, request, context):
        pass

    def cms(self, app):
        return app.cms

    def get_html_body_template(self, app):
        '''Fetch the HTML template for the body part of this request
        '''
        cms = self.cms(app)
        template = (cms.template(self.full_route.path) or
                    self.html_body_template)
        if not template:
            if self.parent:
                template = self.parent.get_html_body_template(app)
            else:
                template = 'home.html'
        return template

    def childname(self, prefix):
        '''key for a child router
        '''
        return '%s%s' % (self.name, prefix) if self.name else prefix

    def make_router(self, rule, **params):
        '''Create a new :class:`.Router` form rule and parameters
        '''
        params.setdefault('cls', HtmlRouter)
        return super().make_router(rule, **params)

    def add_api_urls(self, request, api):
        for r in self.routes:
            if isinstance(r, Router):
                r.add_api_urls(request, api)

    def angular_page(self, app, router, page):
        '''Add angular router information (lux.extensions.angular)
        '''
        if router.route.variables:
            params = dict(((v, v) for v in router.route.variables))
            url = router.route.url(**params)
        else:
            url = page['url']
        page['templateUrl'] = '%s?template=ui' % url


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


def error_handler(request, exc):
    '''Default renderer for errors.'''
    app = request.app
    response = request.response
    if not response.content_type:
        content_type = request.get('default.content_type')
        if content_type:
            response.content_type = request.content_types.best_match(
                content_type)
    content_type = None
    if response.content_type:
        content_type = response.content_type.split(';')[0]
    is_html = content_type == 'text/html'

    if app.debug:
        msg = render_error_debug(request, exc, is_html)
    else:
        msg = error_messages.get(response.status_code) or str(exc)
        if is_html:
            msg = app.render_template(['%s.html' % response.status_code,
                                       'error.html'],
                                      {'status_code': response.status_code,
                                       'status_message': msg})
    #
    if is_html:
        doc = request.html_document
        doc.head.title = response.status
        doc.body.append(msg)
        return doc.render(request)
    elif content_type in JSON_CONTENT_TYPES:
        return json.dumps({'status': response.status_code,
                           'message': msg})
    else:
        return '\n'.join(msg) if isinstance(msg, (list, tuple)) else msg
