import json
from lux import forms
from lux.forms import Layout, Fieldset, Submit, formreg
from lux.extensions.rest import UniqueField


class ApplicationConfigForm(forms.Form):
    DOCKER_USER = forms.EmailField(required=False)
    DOCKER_EMAIL = forms.CharField(required=False)
    DOCKER_PASSWORD = forms.PasswordField(required=False)
    AWS_KEY = forms.CharField(required=False)
    AWS_SECRET = forms.CharField(required=False)


class ApplicationForm(forms.Form):
    id = forms.CharField(readonly=True, required=False)
    name = forms.SlugField(
        minlength=2,
        maxlength=32,
        validator=UniqueField
    )
    domain = forms.CharField(
        minlength=2,
        maxlength=120,
        required=False,
        validator=UniqueField
    )
    config = forms.JsonField(
        required=False,
        ace=json.dumps({'mode': 'json'})
    )


# FORM REGISTRATION
formreg['create-application'] = Layout(
    ApplicationForm,
    Fieldset(all=True),
    Submit('Add new application')
)

formreg['application-config'] = Layout(
    ApplicationConfigForm,
    Fieldset(all=True),
    Submit('Add new application')
)
