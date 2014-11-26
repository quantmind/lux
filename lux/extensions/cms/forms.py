from lux import forms


class PageForm(forms.Form):
    url = forms.CharField()
    title = forms.TextField()
    description = forms.TextField()
    body = forms.TextField()
