import lux
from lux import Parameter
from lux.extensions.angular import add_ng_modules

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
           'PullRepo']


class Extension(lux.Extension):
    _config = [
        Parameter('STATIC_LOCATION', 'build',
                  'Directory where the static site is created')
        ]

    def on_config(self, app):
        app.require('lux.extensions.rest')

    def context(self, request, context):
        if request.cache.html_main:
            context['html_main'] = request.cache.html_main
        return context
