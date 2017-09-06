from collections import Mapping

from pulsar.apps import wsgi
from pulsar.apps.wsgi import wsgi_cached
from pulsar.utils.structures import mapping_iterator

from ..utils.data import unique_tuple


TEXT_CONTENT_TYPES = unique_tuple(('text/html', 'text/plain'))
ERROR_MESSAGES = {
    422: 'Validation Error'
}


class LuxContext(dict):
    pass


class WsgiRequest(wsgi.WsgiRequest):
    """Extend pulsar :class:`~pulsar.apps.wsgi.wrappers.WsgiRequest` with
    additional methods and attributes.
    """
    def __repr__(self):
        return self.first_line

    @property
    def app(self):
        """The :class:`.Application` running the website.
        """
        return self.cache.app

    @property
    def cms(self):
        """The :class:`.Application` running the website.
        """
        return self.cache.app.cms

    @property
    def config(self):
        """The :attr:`.Application.config` dictionary
        """
        return self.cache.app.config

    @property
    def api(self):
        """handler to a Lux API server for this request
        """
        api = self.app.api
        if api:
            return api(self)

    @property
    def http(self):
        return self.cache.http or self.cache.app.http()

    @property
    def cache_server(self):
        return self.cache.app.cache_server

    @wsgi_cached
    def html_document(self):
        """The HTML document for this request
        """
        return self.app.cms.html_document(self)

    @property
    def scheme(self):
        """Protocol scheme, one of ``http`` and ``https``
        """
        return 'https' if self.is_secure else 'http'


wsgi.set_wsgi_request_class(WsgiRequest)


class HeadMeta:
    """Wrapper for HTML5 head metatags.

     Handle meta tags and the Object graph protocol (OGP_)

    .. _OGP: http://ogp.me/
    """
    def __init__(self, head):
        self.head = head
        self.namespaces = {}

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

    def set(self, entry, content):
        """Set the a meta tag with ``content`` and ``entry`` in the HTML5 head.
        The ``key`` for ``entry`` is either ``name`` or ``property`` depending
        on the value of ``entry``.
        """
        content = self.as_string(content)
        if not content:
            return
        if entry == 'title':
            self.head.title = content
            return
        namespace = None
        bits = entry.split(':')
        if len(bits) > 1:
            namespace = bits[0]
            entry = ':'.join(bits[1:])
        if namespace:
            if namespace not in self.namespaces:
                self.namespaces[namespace] = {}
            self.namespaces[namespace][entry] = content
        else:
            self.head.replace_meta(entry, content)

    def get(self, entry, meta_key=None):
        if entry == 'title':
            return self.head.title
        else:
            return self.head.get_meta(entry, meta_key=meta_key)

    def as_string(self, content):
        if isinstance(content, Mapping):
            return content.get('name')
        elif isinstance(content, (list, tuple)):
            return ', '.join(self._list_as_string(content))
        elif content:
            return content

    def _list_as_string(self, content_list):
        for c in content_list:
            c = self.as_string(c)
            if c:
                yield c
