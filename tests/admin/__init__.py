import lux
from lux import forms
from lux.extensions.admin import register, CRUDAdmin

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.auth',
              'lux.extensions.angular',
              'lux.extensions.admin']

HTML5_NAVIGATION = True
API_URL = 'api'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend',
                           'lux.extensions.auth.SessionBackend']


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
