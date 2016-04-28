import os
import json

from pulsar.utils.slugify import slugify
from pulsar.apps.wsgi import MediaRouter

from lux.core import Parameter, LuxExtension
from lux.utils.data import update_dict

from .models import Content, Snippet, snippets_url
from .views import ContentCRUD, SnippetCRUD
from .cms import TextRouter, TextCMS, CMS
from .github import GithubHook, EventHandler, PullRepo


__all__ = ['Content',
           'TextRouter',
           'TextCMS',
           'ContentCRUD',
           'CMS',
           'GithubHook',
           'EventHandler',
           'PullRepo',
           'html_contents']


class Extension(LuxExtension):
    _config = [
        Parameter('CONTENT_REPO', None,
                  'Directory where content repo is located'),
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
        # Add models
        setup_content_models(app)

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
            app.cms = CMS(app)

            for content in html_contents(app):
                app.cms.add_router(content)

            app._handler.middleware.extend(app.cms.middleware())

    def middleware(self, app):
        repo = app.config['CONTENT_REPO']
        if not repo or not os.path.isdir(repo):
            return
        secret = app.config['GITHUB_HOOK_KEY']
        middleware = []
        #
        # Add github hook if the secret is specified
        if secret:
            middleware.append(GithubHook('/refresh-content',
                                         handle_payload=PullRepo(repo),
                                         secret=secret))
        content_config(app)
        return middleware

    def api_sections(self, app):
        """API sections, available whe API_URL is a relative path
        """
        snippet = app.models.get(snippets_url)
        if snippet:
            yield SnippetCRUD(snippet)
        for model in html_contents(app):
            yield ContentCRUD(model)

    def get_template_full_path(self, app, name):
        repo = content_location(app)
        if repo:
            return os.path.join(repo, 'templates', name)


def html_contents(app):
    contents = sorted(app.models.values(), key=lambda c: c.html_url or '')
    for content in reversed(contents):
        if content.html_url is not None and isinstance(content, Content):
            yield content


def setup_content_models(app):
    config = content_config(app)

    if not config:
        return

    # Redirects
    site = config.get(app.meta.name)
    if site:
        app.require('lux.extensions.base')
        app.config['REDIRECTS'].update(site.get('redirects', ()))

    location = config.pop('location')
    # content metadata
    meta = config.pop('meta', {})

    if not app.config['CONTENT_PARTIALS']:
        path = os.path.join(location, 'context')
        if os.path.isdir(path):
            app.config['CONTENT_PARTIALS'] = path

    app.models.register(Snippet('snippet'))

    for loc, cfg in config.pop('paths', {}).items():
        path = cfg.pop('path', loc)
        cfg = update_dict(meta, cfg)
        model = Content(loc, location, path=path, content_meta=cfg)
        app.models.register(model)


def content_location(app):
    repo = app.config['CONTENT_REPO']
    if repo:
        location = app.config['CONTENT_LOCATION']
        if location:
            repo = os.path.join(repo, location)
    return repo


def content_config(app):
    location = content_location(app)
    if not location:
        return

    config = os.path.join(location, 'config.json')
    if not os.path.isfile(config):
        return

    with open(config) as fp:
        cfg = json.load(fp)

    cfg['location'] = location
    return cfg
