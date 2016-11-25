import json

from lux import forms
from lux.core import AuthenticationError
from lux.forms import Layout, Fieldset, Submit, formreg
from lux.extensions.rest import RelationshipField, UniqueField
from lux.extensions.rest.views.forms import PasswordForm
from lux.extensions.rest import validate_policy


class PermissionForm(forms.Form):
    model = 'permissions'
    name = forms.CharField()
    description = forms.TextField(required=False, rows=2)
    policy = forms.JsonField(lux_ace=json.dumps({'mode': 'json'}))

    def clean(self):
        if 'policy' in self.cleaned_data:
            policy = self.cleaned_data['policy']
            self.cleaned_data['policy'] = validate_policy(policy)


class GroupForm(forms.Form):
    model = 'groups'
    name = forms.SlugField(validator=UniqueField())
    permissions = RelationshipField('permissions',
                                    multiple=True,
                                    required=False)


class UserForm(forms.Form):
    username = forms.SlugField()
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    superuser = forms.BooleanField()
    active = forms.BooleanField()
    joined = forms.DateTimeField(readonly=True, required=False)
    groups = RelationshipField('groups', multiple=True, required=False)


class ChangePasswordForm(PasswordForm):
    old_password = forms.PasswordField()

    def clean_old_password(self, value):
        request = self.request
        user = request.cache.user
        auth_backend = request.cache.auth_backend
        try:
            if user.is_authenticated():
                auth_backend.authenticate(request, user=user, password=value)
            else:
                raise AuthenticationError('not authenticated')
        except AuthenticationError as exc:
            raise forms.ValidationError(str(exc))
        return value


class NewTokenForm(forms.Form):
    """Create a new Authorization ``Token`` for the authenticated ``User``.
    """
    description = forms.TextField(minlength=2, maxlength=256)


#
# HTML FORM REGISTRATION
formreg['user'] = Layout(
    UserForm,
    Fieldset(all=True),
    Submit('Update user')
)

formreg['user-profile'] = formreg['user']


formreg['create-group'] = Layout(
    GroupForm,
    Fieldset(all=True),
    Submit('Create new group')
)


formreg['group'] = Layout(
    GroupForm,
    Fieldset(all=True),
    Submit('Update group')
)


formreg['create-permission'] = Layout(
    PermissionForm,
    Fieldset(all=True),
    Submit('Create new permissions')
)


formreg['permission'] = Layout(
    PermissionForm,
    Fieldset(all=True),
    Submit('Update permissions')
)


formreg['create-token'] = Layout(
    NewTokenForm,
    Fieldset(all=True),
    Submit('Create new token')
)
