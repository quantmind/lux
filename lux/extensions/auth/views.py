from datetime import datetime, timedelta

from lux import route
from lux.extensions import rest
from lux.extensions.odm import CRUD, RestRouter, RestModel
from lux.forms import Layout, Fieldset, Submit

from pulsar import MethodNotAllowed
from pulsar.apps.wsgi import Json

from .forms import (permission_model, group_model, user_model,
                    registration_model, CreateUserForm, ChangePasswordForm)


class PermissionCRUD(CRUD):
    _model = permission_model()


class GroupCRUD(CRUD):
    _model = group_model()


class RegistrationCRUD(RestRouter):
    _model = registration_model()

    def get(self, request):
        odm = request.app.odm()
        with odm.begin() as session:
            user = self.get_instance(request, session)
            self.check_model_permission(request, rest.READ)

    def post(self, request):
        model = self.model(request)
        if not model.form:
            raise MethodNotAllowed
        odm = request.app.odm()
        data, _ = request.data_and_files()
        form = model.form(request, data=data)
        if form.is_valid():
            expiry = form.cleaned_data.get('expiry')
            if not expiry:
                days = request.config['ACCOUNT_ACTIVATION_DAYS']
                expiry = datetime.now() + timedelta(days=days)
            with odm.begin() as session:
                user = self.parent.parent.get_instance(request, session)
                reg = odm.registration(user_id=user.id, expiry=expiry,
                                       confirmed=False)
                session.add(reg)
            data = self.serialise(request, reg)
            request.response.status_code = 201
        else:
            data = form.tojson()
        return Json(data).http_response(request)

    @route('<reg_id>', method=('get', 'post', 'put', 'options'))
    def read_update_delete(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response


class UserCRUD(CRUD):
    _model = user_model()
    _registration_model = RestModel('registration')

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        route = self.get_route('read_update_delete')
        route.add_child(RegistrationCRUD())

    def create_model(self, request, data):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)


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
