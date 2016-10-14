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
        "google": ...,
        "twitter": ...,
    }

This extension adds open graph meta tags when the :setting:`DEFAULT_OG_TYPE`
is not ``None`` (it is set to ``website`` by default).

.. _OAuth2: http://oauth.net/2/
.. _OGP: http://ogp.me/
'''
from importlib import import_module

from pulsar.utils.httpurl import is_succesful

from lux.core import Parameter, LuxExtension

from .oauth import get_oauths, request_oauths
from .ogp import OGP
from .views import OAuthRouter, oauth_context


def _import(*names):
    for name in names:
        import_module('lux.extensions.oauth.%s' % name)


_import('amazon', 'dropbox', 'facebook', 'github', 'google', 'linkedin',
        'twitter')


class Extension(LuxExtension):

    _config = [Parameter('OAUTH_PROVIDERS', None,
                         'Dictionary of dictionary of OAuth providers'),
               Parameter('DEFAULT_OG_TYPE', 'website',
                         'Default object graph protocol type. '
                         'Set to None to disable OGP'),
               Parameter('CANONICAL_URL', True,
                         'Add canonical meta tag to website. '
                         'Can be a function or False')]

    def middleware(self, app):
        for auth in get_oauths(app).values():
            if auth.available():
                return [OAuthRouter('oauth')]

    def on_html_document(self, app, request, doc):
        if not is_succesful(request.response.status_code):
            return
        canonical = app.config['CANONICAL_URL']
        if hasattr(canonical, '__call__'):
            canonical = canonical(request, doc)
        if canonical:
            if not isinstance(canonical, str):
                canonical = request.absolute_uri()
            doc.head.links.append(canonical, rel='canonical')

        type = app.config['DEFAULT_OG_TYPE']
        # add canonical if not available
        if type:
            # add default OGP entries
            doc.meta['og:type'] = type
            if canonical:
                doc.meta['og:url'] = canonical
            doc.meta['og:locale'] = app.config['LOCALE']
            doc.meta['og:site_name'] = app.config['APP_NAME']
            oauths = request_oauths(request)
            if oauths:
                for provider in oauths.values():
                    provider.on_html_document(request, doc)
                doc.before_render(self.meta_add_tags)

    def context(self, request, ctx):
        """Add the ``oauth`` callable to the context dictionary
        """
        ctx['oauths'] = lambda: oauth_context(request)

    def meta_add_tags(self, request, doc):
        '''Add meta tags to the html document just before rendering
        '''
        with OGP(doc) as ogp:
            if request:
                oauth = request.cache.oauths
                for provider in oauth.values():
                    provider.ogp_add_tags(request, ogp)
