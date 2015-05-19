import lux
from lux import forms
from lux.extensions.admin import register, CRUDAdmin


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.admin']


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
