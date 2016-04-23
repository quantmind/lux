import json

from lux import forms
from lux.extensions import odm
from lux.extensions.rest import AuthenticationError, RestColumn
from lux.extensions.rest.views.forms import PasswordForm, CreateUserForm
from lux.extensions.rest.policy import validate_policy
from lux.utils.auth import ensure_authenticated


full_name = RestColumn('full_name', displayName='name',
                       field=('first_name', 'last_name', 'username', 'email'))


def permission_model():
    return odm.RestModel('permission', PermissionForm, PermissionForm,
                         repr_field='name')


def group_model():
    model = odm.RestModel('group',
                          GroupForm,
                          GroupForm,
                          repr_field='name')
    model.add_related_column('permissions', permission_model)
    return model


def user_model():
    model = UserModel('user',
                      CreateUserForm,
                      UserForm,
                      id_field='username',
                      repr_field='name',
                      exclude=('password',),
                      columns=(full_name,))
    model.add_related_column('groups', group_model)
    return model


def registration_model():
    return odm.RestModel('registration',
                         RegistrationForm,
                         exclude=('user_id',))


def mailing_list_model():
    model = odm.RestModel('mailinglist', url='mailinglist')
    model.add_related_column('user', user_model, 'user_id')
    return model


class UserModel(odm.RestModel):

    def create_model(self, request, data, session=None):
        '''Override create model so that it calls the backend method
        '''
        if session:
            data['odm_session'] = session
        return request.cache.auth_backend.create_user(request, **data)


class TokenModel(odm.RestModel):
    """REST model for tokens
    """
    @classmethod
    def create(cls, user_model):
        TokenForm = forms.create_form(
            'TokenForm',
            forms.TextField('description', required=True, maxlength=256))
        model = cls('token', TokenForm)
        model.add_related_column('user', user_model, 'user_id')
        return model

    def create_model(self, request, data, session=None):
        user = ensure_authenticated(request)
        auth = request.cache.auth_backend
        data['session'] = False
        return auth.create_token(request, user, **data)


class PermissionForm(forms.Form):
    model = 'permission'
    id = forms.HiddenField(required=False)
    name = forms.CharField()
    description = forms.TextField()
    policy = forms.JsonField(text_edit=json.dumps({'mode': 'json'}))

    def clean(self):
        policy = self.cleaned_data['policy']
        self.cleaned_data['policy'] = validate_policy(policy)


class GroupForm(forms.Form):
    model = 'group'
    id = forms.HiddenField(required=False)
    name = forms.SlugField(validator=odm.UniqueField())
    permissions = odm.RelationshipField(permission_model,
                                        multiple=True,
                                        required=False)


class UserForm(forms.Form):
    id = forms.HiddenField(required=False)
    username = forms.SlugField()
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    superuser = forms.BooleanField()
    active = forms.BooleanField()
    joined = forms.DateTimeField(readonly=True, required=False)
    groups = odm.RelationshipField(group_model,
                                   multiple=True,
                                   required=False)


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
