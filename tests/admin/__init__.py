import lux
from lux import forms
from lux.extensions import rest
from lux.extensions.admin import register, CRUDAdmin


from tests.config import *  # noqa


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.auth',
              'lux.extensions.odm',
              'lux.extensions.angular',
              'lux.extensions.admin']

API_URL = 'api'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
DEFAULT_PERMISSION_LEVELS = {}
DEFAULT_PERMISSION_LEVEL = rest.DELETE


class Extension(lux.Extension):
    pass


class BlogForm(forms.Form):
    title = forms.CharField()
    author = forms.CharField()
    body = forms.TextField()


@register('blog')
class BlogAdmin(CRUDAdmin):
    icon = 'fa fa-book'
    form = forms.Layout(BlogForm)
