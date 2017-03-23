'''The base :ref:`lux extension <writing-extensions>` provides several
middleware utilities. If used, it should be the first extension in your
:setting:`EXTENSIONS` list (excluding extensions which
don't provide any wsgi middleware such as :mod:`lux.extensions.sitemap`
for example).

Media Handling
======================
When the :setting:`SERVE_STATIC_FILES` parameter is set to ``True``,
this extension adds middleware for serving static files from
:setting:`MEDIA_URL`.
In addition, a :setting:`HTML_FAVICON` location can also be specified.
'''
import os
import hashlib
from urllib.parse import urlparse

from pulsar.apps import wsgi
from pulsar.utils.httpurl import remove_double_slash, is_absolute_uri

from lux.core import LuxExtension, Parameter, RedirectRouter


class Extension(LuxExtension):
    _config = [
        Parameter('GZIP_MIN_LENGTH', None,
                  'If a positive integer, a response middleware is added so '
                  'that it encodes the response via the gzip algorithm.'),
        Parameter('USE_ETAGS', False, ''),
        Parameter('CLEAN_URL', False,
                  'When ``True``, requests on urls with consecutive slashes '
                  'are converted to valid url and redirected.'),
        Parameter('REDIRECTS', {},
                  'Dictionary mapping url to another url to redirect to.'),
        Parameter('SERVE_STATIC_FILES', False,
                  'if ``True`` add middleware to serve static files.'),
        Parameter('HTML_FAVICON', None,
                  'Adds tag of type ``image/x-icon`` in the head section of'
                  ' the Html document')]

    def middleware(self, app):
        '''Add two middleware handlers if configured to do so.'''
        middleware = []
        if app.config['CLEAN_URL']:
            middleware.append(wsgi.clean_path_middleware)
        path = app.config['MEDIA_URL']

        if is_absolute_uri(path):
            app.config['SERVE_STATIC_FILES'] = False

        if os.path.isdir(app.config['SERVE_STATIC_FILES'] or ''):
            if path.endswith('/'):
                path = path[:-1]
            location = app.config['SERVE_STATIC_FILES']
            middleware.append(wsgi.MediaRouter(path, location,
                                               show_indexes=app.debug))

        if app.config['REDIRECTS']:
            for url, to in app.config['REDIRECTS'].items():
                middleware.append(RedirectRouter(url, to))

        return middleware

    def response_middleware(self, app):
        gzip = app.config['GZIP_MIN_LENGTH']
        middleware = []
        if gzip:
            middleware.append(wsgi.GZipMiddleware(gzip))
        if app.config['USE_ETAGS']:
            middleware.append(self.etag)
        return middleware

    def on_html_document(self, app, request, doc):
        favicon = app.config['HTML_FAVICON']
        if favicon:
            parsed = urlparse(favicon)
            if not parsed.scheme and not parsed.netloc:
                media = app.config['MEDIA_URL']
                if not favicon.startswith(media):
                    favicon = remove_double_slash('%s%s' % (media, favicon))
            doc.head.links.append(favicon, rel="icon",
                                  type='image/x-icon')

    def etag(self, environ, response):
        if response.has_header('ETag'):
            etag = response['ETag']
        elif response.streaming:
            etag = None
        else:
            etag = '"%s"' % hashlib.md5(response.content).hexdigest()
        if etag is not None:
            if (200 <= response.status_code < 300 and
                    environ.get('HTTP_IF_NONE_MATCH') == etag):
                response.not_modified()
            else:
                response['ETag'] = etag
        return response
