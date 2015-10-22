from lux import route
from lux.extensions import rest
from lux.extensions.odm import CRUD, RestModel
from lux.forms import Layout, Fieldset, Submit

from .forms import (permission_model, group_model, user_model, CreateUserForm,
                    ChangePasswordForm)


class PermissionCRUD(CRUD):
    _model = permission_model()


class GroupCRUD(CRUD):
    _model = group_model()


class RegistrationCRUD(CRUD):
    _model = RestModel('registration')


class UserCRUD(CRUD):
    _model = user_model()
    _registration_model = RestModel('registration')

    def create_model(self, request, data):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)

    @route('<id>/registrations', method=('get', 'options', 'post'))
    def registrations(self, request):
        odm = request.app.odm()
        with odm.begin() as session:
            user = self.get_instance(request, session)
            if request.method == 'GET':
                self.check_model_permission(request, rest.READ,
                                            self._registration_model)
            elif request.method == 'POST':
                pass
            else:
                pass

    @route('<id>/registrations/<reg_id>',
           method=('get', 'post', 'put', 'options'))
    def registration(self, request):
        odm = request.app.odm()
        with odm.begin() as session:
            user = self.get_instance(request, session)
            if request.method == 'GET':
                self.check_model_permission(request, rest.READ,
                                            self._registration_model)
                data = session.query(odm.registration).filter_by(
                    user_id=user.id).all()

            elif request.method == 'POST':
                pass
            else:
                pass


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
