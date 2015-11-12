import json

from sqlalchemy.exc import DataError

from lux import forms
from lux.extensions import odm
from lux.extensions.rest import AuthenticationError, RestColumn
from lux.extensions.rest.forms import PasswordForm
from lux.extensions.rest.policy import validate_policy

__all__ = ['permission_model',
           'group_model',
           'user_model',
           'TokenModel',
           'PermissionForm',
           'GroupForm',
           'UserForm',
           'CreateUserForm',
           'ChangePasswordForm']


full_name = RestColumn('full_name', displayName='name',
                       field=('first_name', 'last_name', 'username', 'email'))


def permission_model():
    return odm.RestModel('permission', PermissionForm, repr_field='name')


def group_model():
    model = odm.RestModel('group', GroupForm, repr_field='name')
    model.add_related_column('permissions', permission_model)
    return model


def user_model():
    return UserModel('user',
                     CreateUserForm,
                     UserForm,
                     id_field='username',
                     repr_field='name',
                     exclude=('password',),
                     columns=(full_name,
                              odm.ModelColumn('groups', group_model)))


def registration_model():
    return odm.RestModel('registration',
                         RegistrationForm,
                         exclude=('user_id',))


class UserModel(odm.RestModel):

    def create_model(self, request, data, session=None):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)


class TokenModel(odm.RestModel):

    def create_model(self, request, data, session=None):
        auth = request.cache.auth_backend
        user = data.pop('user', None)
        if user:
            return auth.create_token(request, user, **data)
        else:
            raise DataError('Missing user')


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
    username = forms.CharField()
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    superuser = forms.BooleanField()
    active = forms.BooleanField()
    joined = forms.DateTimeField(readonly=True, required=False)
    groups = odm.RelationshipField(group_model,
                                   multiple=True,
                                   required=False)


class CreateUserForm(PasswordForm):
    '''Form for creating a new user form username, email and password
    '''
    model = 'user'
    username = forms.CharField(required=True,
                               validator=odm.UniqueField(),
                               maxlength=30)
    email = forms.EmailField(required=True,
                             validator=odm.UniqueField())

    def clean_username(self, value):
        request = self.request
        if request.config['CHECK_USERNAME'](request, value):
            return value
        else:
            raise forms.ValidationError('Username not available')


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
