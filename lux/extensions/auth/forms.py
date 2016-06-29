import json

from lux import forms
from lux.forms import Layout, Fieldset, Submit, formreg
from lux.extensions.odm import RestModel
from lux.extensions.rest import (AuthenticationError, RestField,
                                 RelationshipField, UniqueField)
from lux.extensions.rest.views.forms import PasswordForm
from lux.extensions.rest.policy import validate_policy
from lux.utils.auth import ensure_authenticated


full_name = RestField(
    'full_name',
    displayName='Name',
    field=('first_name', 'last_name', 'username', 'email')
)


# REST Models
class UserModelBase(RestModel):

    @classmethod
    def create(cls, url=None, exclude=None, hidden=None, fields=None):
        exclude = exclude or ('password',)
        fields = list(fields or ())
        fields.extend((
            full_name,
            RestField('groups', model='groups')
        ))
        return cls(
            'user',
            'create-user',
            'user',
            url=url,
            id_field='username',
            repr_field='full_name',
            exclude=exclude,
            hidden=hidden,
            fields=fields
        )


class UserModel(UserModelBase):

    def create_model(self, request, instance, data, session=None):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)


class RequestUserModel(UserModelBase):

    @classmethod
    def create(cls, exclude=None, hidden=None, fields=None):
        exclude = exclude or ('password',)
        fields = list(fields or ())
        fields.extend((
            full_name,
            RestField('groups', model='groups')
        ))
        return cls(
            'user',
            updateform='user-profile',
            url='user',
            id_field='username',
            repr_field='full_name',
            exclude=exclude,
            hidden=hidden,
            fields=fields
        )

    def get_instance(self, request, *args, **kwargs):
        return self.instance(ensure_authenticated(request))


class TokenModel(RestModel):
    """REST model for tokens
    """
    @classmethod
    def create(cls):
        return cls(
            'token',
            'create-token',
            fields=[
                RestField('user', field='user_id', model='users')
            ]
        )

    def create_model(self, request, instance, data, session=None):
        user = ensure_authenticated(request)
        auth = request.cache.auth_backend
        data['session'] = False
        return auth.create_token(request, user, **data)


# FORMS
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


class RegistrationForm(forms.Form):
    expiry = forms.DateTimeField(required=False)


class NewTokenForm(forms.Form):
    """Form to create tokens for the current user
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
    Submit('Create token')
)
