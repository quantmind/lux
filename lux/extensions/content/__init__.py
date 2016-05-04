import os

from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import MediaRouter

from lux.core import Parameter, LuxExtension

from .models import ContentModel
from .views import ContentCRUD
from .cms import TextRouter, TextCMS, CMS, CmsContent
from .github import GithubHook, EventHandler, PullRepo
from .utils import content_location


__all__ = ['Content',
           'CmsContent',
           'TextRouter',
           'TextCMS',
           'ContentCRUD',
           'CMS',
           'GithubHook',
           'EventHandler',
           'PullRepo']


class Extension(LuxExtension):
    _config = [
        Parameter('CONTENT_REPO', None,
                  'Directory where content repo is located'),
        Parameter('CONTENT_MODELS', None,
                  'Structure of content'),
        Parameter('CONTENT_PARTIALS', None,
                  'Path to CMS Partials snippets'),
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
