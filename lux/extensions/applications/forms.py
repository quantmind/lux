import json
from lux import forms
from lux.forms import Layout, Fieldset, Submit, formreg
from lux.extensions.odm import RestModel
from lux.utils.crypt import create_uuid


class ApplicationConfigForm(forms.Form):
    docker_user = forms.EmailField(required=False)
    docker_email = forms.CharField(required=False)
    docker_password = forms.PasswordField(required=False)
    aws_key = forms.CharField(required=False)
    aws_secret = forms.CharField(required=False)


class ApplicationForm(forms.Form):
    id = forms.CharField(readonly=True, required=False)
    name = forms.SlugField(minlength=2, maxlength=32)
    config = forms.JsonField(required=False,
                             ace=json.dumps({'mode': 'json'}))


class LightStreamRestModel(RestModel):

    def create_model(self, request, instance, data, session=None):
        model = self.instance(instance).obj
        model.id = create_uuid()
        return super().create_model(request, instance, data, session=session)


# FORM REGISTRATION
formreg['create-application'] = Layout(
    ApplicationForm,
    Fieldset(all=True),
    Submit('Add new application')
)
