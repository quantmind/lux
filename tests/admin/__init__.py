from lux import forms
from lux.core import LuxExtension

from lux.extensions.admin import register, CRUDAdmin
from lux.extensions.odm import CRUD, RestModel


from tests.config import *  # noqa


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.auth',
              'lux.extensions.odm',
              'lux.extensions.angular',
              'lux.extensions.admin']

API_URL = 'http://api.com'
DEFAULT_CONTENT_TYPE = 'text/html'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
DEFAULT_PERMISSION_LEVELS = {}
DEFAULT_PERMISSION_LEVEL = '*'


class Extension(LuxExtension):

    def api_sections(self, app):
        return [CRUD(RestModel('blog', 'blog', 'blog', url='blog'))]

    def on_loaded(self, app):
        app.forms['blog'] = forms.Layout(BlogForm)


class BlogForm(forms.Form):
    title = forms.CharField()
    author = forms.CharField()
    body = forms.TextField()


@register('blog')
class BlogAdmin(CRUDAdmin):
    icon = 'fa fa-book'
    form = 'blog'
