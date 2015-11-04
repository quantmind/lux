from datetime import datetime, timedelta

from lux import route
from lux.extensions import rest
from lux.extensions.rest.htmlviews import SignUp as SignUpView
from lux.extensions.odm import CRUD, RestRouter
from lux.forms import Layout, Fieldset, Submit

from pulsar import MethodNotAllowed, Http404
from pulsar.apps.wsgi import Json

from .forms import (permission_model, group_model, user_model,
                    registration_model, CreateUserForm, ChangePasswordForm)


class PermissionCRUD(CRUD):
    _model = permission_model()


class GroupCRUD(CRUD):
    _model = group_model()


class RegistrationCRUD(RestRouter):
    get_user = None
    '''Function to retrieve user from url
    '''
    _model = registration_model()

    def get(self, request):
        odm = request.app.odm()
        with odm.begin() as session:
            # user = self.get_instance(request, session)
            self.check_model_permission(request, rest.READ)

    def post(self, request):
        '''Create a new authentication key
        '''
        model = self.model(request)
        if not model.form or not self.get_user:
            raise MethodNotAllowed
        data, _ = request.data_and_files()
        form = model.form(request, data=data)
        if form.is_valid():
            expiry = form.cleaned_data.get('expiry')
            if not expiry:
                days = request.config['ACCOUNT_ACTIVATION_DAYS']
                expiry = datetime.now() + timedelta(days=days)
            user = self.get_user(request)
            # TODO, this is for multirouters
            if isinstance(user, tuple):
                user = user[0]
            backend = request.cache.auth_backend
            auth_key = backend.create_auth_key(request, user, expiry=expiry)
            data = {'registration_key': auth_key}
            request.response.status_code = 201
        else:
            data = form.tojson()
        return Json(data).http_response(request)


class UserCRUD(CRUD):
    _model = user_model()

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        route = self.get_route('read_update_delete')
        route.add_child(RegistrationCRUD(get_user=self.get_instance))

    def create_model(self, request, data):
        '''Override create model so that it calls the backend method
        '''
        return request.cache.auth_backend.create_user(request, **data)

    @route('authkey', position=-99, method=('get', 'options'))
    def get_authkey(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        if 'auth_key' in request.url_data:
            auth_key = request.url_data['auth_key']
            backend = request.cache.auth_backend
            user = backend.get_user(request, auth_key=auth_key)
            if user:
                return self.collection_response(request, id=user.id)

        raise Http404


class Authorization(rest.Authorization):
    '''Override Authorization router with a new create_user_form
    '''
    create_user_form = CreateUserForm
    change_password_form = ChangePasswordForm


class SignUp(SignUpView):
    '''Handle sign up on Html pages
    '''
    default_form = Layout(CreateUserForm,
                          Fieldset('username', 'email', 'password',
                                   'password_repeat'),
                          Submit('Sign up',
                                 disabled="form.$invalid"),
                          showLabels=False,
                          directive='user-form')
