'''\
This extension facilitates login via third party authentication providers
using either the OAuth1 or OAuth2_ protocol.
In addition, it allows the use of the Open Graph Protocol (OGP_) for social
graphs and twitter cards and  additional APIs a provider may have
(google analytics, google map for example).

Usage
==========

Add :mod:`lux.extensions.oauth` to the :setting:`EXTENSIONS` list of your
project and include the :setting:`OAUTH_PROVIDERS` dictionary::

    OAUTH_PROVIDERS = {
        'google': ...,
        'twitter': ...,
    }

This extension adds open graph meta tags when the :setting:`DEFAULT_OG_TYPE`
is not ``None`` (it is set to ``website`` by default).

.. _OAuth2: http://oauth.net/2/
.. _OGP: http://ogp.me/
'''
from importlib import import_module

import lux
from lux import Parameter
from lux.core.wrappers import HeadMeta

from .oauth import get_oauths
from .ogp import OGP
from .views import OAuthRouter, oauth_context


def _import(*names):
    for name in names:
        import_module('lux.extensions.oauth.%s' % name)


_import('amazon', 'dropbox', 'facebook', 'github', 'google', 'linkedin',
        'twitter')


__all__ = ['OAuthRouter', 'OGP', 'get_oauths']


class Extension(lux.Extension):

    _config = [Parameter('OAUTH_PROVIDERS', None,
                         'Dictionary of dictionary of OAuth providers'),
               Parameter('DEFAULT_OG_TYPE', 'website',
                         'Default object graph protocol type. '
                         'Set to None to disable OGP')]

    def on_html_document(self, app, request, doc):
        doc.meta = NamespaceHeadMeta(doc.head)
        type = app.config['DEFAULT_OG_TYPE']
        if type:
            # add default OGP entries
            doc.meta['og:type'] = type
            doc.meta['og:url'] = app.site_url(request.path)
            doc.meta['og:locale'] = app.config['LOCALE']
            oauths = get_oauths(request)
            if oauths:
                for provider in oauths.values():
                    provider.on_html_document(request, doc)
                doc.before_render(self.meta_add_tags)
        doc.jscontext['oauths'] = oauth_context(request)

    def meta_add_tags(self, request, doc):
        with OGP(doc) as ogp:
            if request:
                oauth = request.cache.oauths
                for provider in oauth.values():
                    provider.ogp_add_tags(request, ogp)


class NamespaceHeadMeta(HeadMeta):
    '''Wrapper for HTML5 head metatags

    Handle meta tags and the Object graph protocol (OGP_)

    .. _OGP: http://ogp.me/
    '''
    def __init__(self, head):
        self.head = head
        self.namespaces = {}

    def set(self, entry, content):
        '''Set the a meta tag with ``content`` and ``entry`` in the HTML5 head.
        The ``key`` for ``entry`` is either ``name`` or ``property`` depending
        on the value of ``entry``.
        '''
        if content:
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
                if isinstance(content, (list, tuple)):
                    content = ', '.join(content)
                self.head.replace_meta(entry, content)
