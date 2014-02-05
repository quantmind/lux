from pulsar.utils.html import slugify, nicename

from lux import forms


def template_choice(bfield):
    '''Generator of ``index, descriptor`` tuples for templates.'''
    request = bfield.request
    if request:
        templates = request.app.config.get('PAGE_TEMPLATES')
        if templates:
            def _():
                for key, template in templates.items():
                    yield key, nicename(key)
            return sorted(_(), key=lambda x: x[0])
    return ()


class PageForm(forms.Form):
    '''The form for editing and adding a new page to the CMS.'''
    url = forms.CharField(widget_attrs={'readonly': 'readonly'})
    title = forms.CharField(required=False)
    body_class = forms.CharField(required=False)
    template = forms.ChoiceField(choices=template_choice)


class ContentForm(forms.Form):
    content_type = forms.CharField()
    title = forms.CharField(required=True)
    slug = forms.HiddenField(required=False)


    layout = forms.Layout(forms.Fieldset('title', show_label=False),
                          forms.Fieldset('body', show_label=False))

    def value_from_instance(self, instance, name, value):
        if name == 'body':
            return instance.data.get('body', '')
        else:
            return getattr(instance, name, value)

    def clean(self):
        data = self.cleaned_data
        slug = data.get('slug')
        if not slug:
            self.cleaned_data['slug'] = slugify(data['title'].lower())
        data['data'] = {'body': data.pop('body', '')}
