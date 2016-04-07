from pulsar.apps.wsgi import MediaRouter
from pulsar.utils.slugify import slugify

import lux
from lux import Parameter

from .models import Content
from .views import TextRouter, TextCMS, ContentCRUD, TextForm, CMS
from .github import GithubHook, EventHandler, PullRepo


__all__ = ['Content',
           'TextRouter',
           'TextCMS',
           'ContentCRUD',
           'CMS',
           'TextForm',
           'GithubHook',
           'EventHandler',
           'PullRepo',
           'html_contents']


class Extension(lux.Extension):
    _config = [
        Parameter('STATIC_LOCATION', None,
                  'Directory where the static site is created')
        ]

    def on_config(self, app):
        app.require('lux.extensions.rest')

    def context(self, request, context):
        if request.cache.html_main:
            context['html_main'] = request.cache.html_main
        context['slug']  = slugify(request.path[1:] or 'index')
        return context

    def on_loaded(self, app):
        if app.callable.command == 'serve_static':
            location = app.config['STATIC_LOCATION']
            app.handler = MediaRouter('', location, default_suffix='html')


def html_contents(app):
    contents = sorted(app.models.values(), key=lambda c: c.html_url or '')
    for content in reversed(contents):
        if content.html_url is not None and isinstance(content, Content):
            yield content
