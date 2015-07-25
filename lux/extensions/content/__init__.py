import lux
from lux.extensions.angular import add_ng_modules

from .models import Content
from .views import TextCRUD, TextForm, CMS
from .ui import add_css
from .github import GithubHook, PullRepo


__all__ = ['Content', 'TextCRUD', 'CMS', 'TextForm', 'add_css',
           'GithubHook', 'PullRepo']


class Extension(lux.Extension):

    def context(self, request, context):
        if request.cache.html_main:
            context['html_main'] = request.cache.html_main
        return context

    def on_html_document(self, app, request, doc):
        add_ng_modules(doc, 'lux.cms')
