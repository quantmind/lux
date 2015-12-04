from datetime import datetime, timedelta

from lux import route
from lux.extensions import rest
from lux.extensions.rest.htmlviews import (SignUp as SignUpView,
                                           ComingSoon as ComingSoonView)
from lux.extensions.odm import CRUD, RestRouter
from lux.forms import Layout, Fieldset, Submit
from lux.extensions.rest.forms import EmailForm
from lux.extensions.rest.authviews import action

from pulsar import MethodNotAllowed, Http404, PermissionDenied
from pulsar.apps.wsgi import Json

from .forms import (permission_model, group_model, user_model,
                    registration_model, CreateUserForm, ChangePasswordForm)


class PermissionCRUD(CRUD):
    _model = permission_model()


class GroupCRUD(CRUD):
    _model = group_model()


class RegistrationCRUD(CRUD):
    get_user = None
    '''Function to retrieve user from url
    '''
    _model = registration_model()

    def get(self, request):
        '''Get a list of models
        '''
        self.check_model_permission(request, rest.READ)
        # Columns the user doesn't have access to are dropped by
        # serialise_model
        return self.model(request).collection_response(request)

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

    @route(method=('get', 'options'))
    def metadata(self, request):
        '''Model metadata
        '''
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        backend = request.cache.auth_backend
        model = self.model(request)

        if backend.has_permission(request, model.name, rest.READ):
            meta = model.meta(request)
            return Json(meta).http_response(request)
        raise PermissionDenied


class UserCRUD(CRUD):
    _model = user_model()

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        route = self.get_route('read_update_delete')
        route.add_child(RegistrationCRUD(get_user=self.get_instance))

    @route('authkey', position=-99, method=('get', 'options'))
    def get_authkey(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response

        if 'auth_key' in request.url_data:
            auth_key = request.url_data['auth_key']
            backend = request.cache.auth_backend
            user = backend.get_user(request, auth_key=auth_key)
            if user:
                model = self.model(request)
                return model.collection_response(request, id=user.id)

        raise Http404


class Authorization(rest.Authorization):
    '''Override Authorization router with a new create_user_form
    '''
    create_user_form = CreateUserForm
    change_password_form = ChangePasswordForm

    @action
    def mailing_list(self, request):
        '''Add a given email to a mailing list
        '''
        user = request.cache.user
        data = request.body_data()
        if user.is_authenticated():
            raise MethodNotAllowed
        form = EmailForm(request, data=data)
        if form.is_valid():
            email = form.cleaned_data['email']
            odm = request.app.odm()
            topic = request.config['GENERAL_MAILING_LIST_TOPIC']
            with odm.begin() as session:
                q = session.query(odm.mailinglist).filter_by(email=email,
                                                             topic=topic)
                if not q.count():
                    entry = odm.mailinglist(email=email, topic=topic)
                    session.add(entry)
                    request.response.status_code = 201
                    result = {'message': ('Email %s added to mailing list'
                                          % email)}
                else:
                    result = {'message': ('Email %s already in mailing list'
                                          % email)}
        else:
            result = form.tojson()
        return Json(result).http_response(request)


class SignUp(SignUpView):
    '''Handle sign up on Html pages
    '''
    default_form = Layout(CreateUserForm,
                          Fieldset('username', 'email', 'password',
                                   'password_repeat'),
                          Submit('Sign up',
                                 disabled="form.$invalid"),
                          showLabels=False,
                          directive='user-form',
                          resultHandler='signUp')


class ComingSoon(ComingSoonView):
    form_enctype = 'application/json'

    def form_action(self, request):
        api = request.config['API_URL']
        return rest.luxrest(api,
                            name='authorizations_url',
                            path='mailing_list')
