import os

from pulsar import Http404
from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import MediaRouter

from lux.core import Parameter, LuxExtension
from lux.extensions.rest import api_path

from .models import ContentModel
from .rest import ContentCRUD
from .cms import TextRouter, CMS, CmsContent, LazyContext
from .github import GithubHook, EventHandler, PullRepo
from .files import content_location
from .static import StaticCache
from .contents import html_partial


__all__ = ['Content',
           'CmsContent',
           'TextRouter',
           'ContentCRUD',
           'CMS',
           'GithubHook',
           'EventHandler',
           'PullRepo',
           'StaticCache',
           'LazyContext']


class Extension(LuxExtension):
    _config = [
        Parameter('CONTENT_GROUPS', None,
                  'List of content model configurations'),
        Parameter('CONTENT_REPO', None,
                  'Directory where content repo is located'),
        Parameter('CONTENT_LOCATION', None,
                  'Directory where content is located inside CONTENT_REPO'),
        Parameter('STATIC_LOCATION', None,
                  'Directory where the static site is created'),
        Parameter('GITHUB_HOOK_KEY', None,
                  'Secret key for github webhook')
    ]

    def on_config(self, app):
        self.require(app, 'lux.extensions.rest')

    def context(self, request, context):
        if request.cache.html_main:
            context['html_main'] = request.cache.html_main
        if 'slug' not in context:
            context['slug'] = slugify(request.path[1:] or 'index')
        return context

    def on_loaded(self, app):
        if app.callable.command == 'serve_static':
            location = app.config['STATIC_LOCATION']
            app._handler = MediaRouter('', location, default_suffix='html')
        #
        # Add HTML middleware if this is a web-site server
        elif app.config['DEFAULT_CONTENT_TYPE'] == 'text/html':
            app.cms = CMS.build(app)

    def api_sections(self, app):
        location = content_location(app)
        if not location:
            return

        secret = app.config['GITHUB_HOOK_KEY']
        middleware = []
        #
        # Add github hook if the secret is specified
        if secret:
            middleware.append(GithubHook('/refresh-content',
                                         handle_payload=PullRepo(location),
                                         secret=secret))
        middleware.append(ContentCRUD(ContentModel(location)))
        return middleware

    def get_template_full_path(self, app, name):
        repo = content_location(app)
        if repo:
            return os.path.join(repo, 'templates', name)

    def html_content(self, request, path, context):
        url = api_path(request, 'contents', path)
        if url:
            try:
                meta = request.api.get(url).json()
            except Http404:
                pass
            app = request.app
            context = app.context(request, context)
            return html_partial(app, meta, context)
