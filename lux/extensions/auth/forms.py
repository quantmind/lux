from lux import forms
from lux.extensions import odm


class PermissionForm(forms.Form):
    id = forms.HiddenField(required=False)
    name = odm.CharField()
    description = odm.TextField()
    policy = odm.JsonField()
