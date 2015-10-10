from lux.extensions import rest
from lux.extensions.odm import CRUD, RestModel
from lux.forms import Layout, Fieldset, Submit

from .forms import (permission_model, group_model, user_model, CreateUserForm,
                    ChangePasswordForm)


class PermissionCRUD(CRUD):
    model = permission_model()


class GroupCRUD(CRUD):
    model = group_model()


class UserCRUD(CRUD):
    model = user_model()

    def create_model(self, request, data):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)


class RegistrationCRUD(CRUD):
    model = RestModel('registration')


class Authorization(rest.Authorization):
    '''Override Authorization router with a new create_user_form
    '''
    create_user_form = CreateUserForm
    change_password_form = ChangePasswordForm


class SignUp(rest.SignUp):
    '''Handle sign up on Html pages
    '''
    default_form = Layout(CreateUserForm,
                          Fieldset('username', 'email', 'password',
                                   'password_repeat'),
                          Submit('Sign up',
                                 disabled="form.$invalid"),
                          showLabels=False,
                          directive='user-form')
