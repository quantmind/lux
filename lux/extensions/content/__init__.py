import lux

from .models import Content
from .views import TextCRUD, TextForm, CMS
from .ui import add_css
from .github import GithubHook


__all__ = ['Content', 'TextCRUD', 'CMS', 'TextForm', 'add_css', 'GithubHook']


class Extension(lux.Extension):

    def context(self, request, context):
        if request.cache.html_main:
            context['html_main'] = request.cache.html_main
        return context
