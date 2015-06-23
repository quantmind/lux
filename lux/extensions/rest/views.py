import json

import lux
from lux import route
from lux.forms import Form

from pulsar import Http404, PermissionDenied, MethodNotAllowed
from pulsar.apps.wsgi import Json

from .forms import LoginForm, CreateUserForm, ChangePasswordForm
from .user import AuthenticationError
from .models import RestModel


REST_CONTENT_TYPES = ['application/json']


def action(f):
    f.is_action = True
    return f


def logout(request):
    form = Form(request, data=request.body_data() or {})

    if form.is_valid():
        user = request.cache.user
        if not user.is_authenticated():
            raise MethodNotAllowed

        auth_backend = request.cache.auth_backend
        return auth_backend.logout_response(request, user)
    else:
        raise MethodNotAllowed


class RestRoot(lux.Router):
    '''Api Root

    Provide a get method for displaying a dictionary of api names - api urls
    key - value pairs
    '''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        for router in self.routes:
            routes[router.model.api_name] = request.absolute_uri(router.path())
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


class RestMixin:
    model = None
    '''Instance of a :class:`~lux.extensions.rest.RestModel`
    '''
    def __init__(self, *args, **kwargs):
        if self.model is None and args:
            self.model, args = args[0], args[1:]

        if not isinstance(self.model, RestModel):
            raise NotImplementedError('REST model not available')

        super().__init__(self.model.url, *args, **kwargs)


class RestRouter(RestMixin, lux.Router):
    response_content_types = REST_CONTENT_TYPES

    def options(self, request):
        '''Handle the CORS preflight request
        '''
        request.app.fire('on_preflight', request)
        return request.response

    def limit(self, request):
        '''The maximum number of items to return when fetching list
        of data'''
        cfg = request.config
        user = request.cache.user
        MAXLIMIT = (cfg['API_LIMIT_AUTH'] if user.is_authenticated() else
                    cfg['API_LIMIT_NOAUTH'])
        try:
            limit = int(request.url_data.get(cfg['API_LIMIT_KEY'],
                                             cfg['API_LIMIT_DEFAULT']))
        except ValueError:
            limit = MAXLIMIT
        return min(limit, MAXLIMIT)

    def offset(self, request):
        '''Retrieve the offset value from the url when fetching list of data
        '''
        cfg = request.config
        try:
            return int(request.url_data.get(cfg['API_OFFSET_KEY'], 0))
        except ValueError:
            return 0

    def query(self, request):
        cfg = request.config
        return request.url_data.get(cfg['API_SEARCH_KEY'], '')

    def serialise(self, request, data):
        if isinstance(data, list):
            return [self.serialise_model(request, o, True) for o in data]
        else:
            return self.serialise_model(request, data)

    def meta(self, request):
        app = request.app
        columns = self.model.columns(app)

        return {'id': self.model.id_field,
                'repr': self.model.repr_field,
                'columns': columns,
                'default-limit': app.config['API_LIMIT_DEFAULT']}

    def serialise_model(self, request, data, in_list=False):
        '''Serialise on model
        '''
        return self.model.tojson(request, data)

    def json(self, request, data):
        '''Return a response as application/json
        '''
        return Json(data).http_response(request)


class ProcessLoginMixin:
    login_form = LoginForm

    def post(self, request):
        '''Authenticate the user
        '''
        # user = request.cache.user
        # if user.is_authenticated():
        #     raise MethodNotAllowed

        form = self.login_form(request, data=request.body_data())

        if form.is_valid():
            auth_backend = request.cache.auth_backend
            try:
                user = auth_backend.authenticate(request, **form.cleaned_data)
                if user.is_active():
                    return auth_backend.login_response(request, user)
                else:
                    return auth_backend.inactive_user_login_response(request,
                                                                     user)
            except AuthenticationError as e:
                form.add_error_message(str(e))

        return Json(form.tojson()).http_response(request)


class Authorization(RestRouter, ProcessLoginMixin):
    '''Authentication views for

    * login
    * logout
    * signup
    * password change
    * password recovery

    All views respond to POST requests
    '''
    model = RestModel('authorization')
    create_user_form = CreateUserForm
    change_password_form = ChangePasswordForm

    @route('/<action>', method=('post', 'options'))
    def auth_action(self, request):
        '''Post actions
        '''
        action = request.urlargs['action']
        method = getattr(self, action, None)
        if not getattr(method, 'is_action', False):
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        return method(request)

    @action
    def logout(self, request):
        # make sure csrf is called
        return logout(request)

    @action
    def signup(self, request):
        '''Handle signup post data

        If :attr:`.create_user_form` form is None, raise a 4040 error.

        A succesful response is returned by the backend
        :meth:`.signup_response` method.
        '''
        if not self.create_user_form:
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed

        form = self.create_user_form(request, data=request.body_data())

        if form.is_valid():
            data = form.cleaned_data
            auth_backend = request.cache.auth_backend
            try:
                user = auth_backend.create_user(request, **data)
                return auth_backend.signup_response(request, user)
            except AuthenticationError as e:
                form.add_error_message(str(e))
        return Json(form.tojson()).http_response(request)

    @action
    def change_password(self, request):
        '''Change user password
        '''
        # Set change_password_form to None to remove support
        # for password change
        if not self.change_password_form:
            raise Http404

        user = request.cache.user
        if not user.is_authenticated():
            raise MethodNotAllowed

        form = self.change_password_form(request, data=request.body_data())

        if form.is_valid():
            auth_backend = request.cache.auth_backend
            password = form.cleaned_data['password']
            auth_backend.set_password(user, password)
            return auth_backend.changed_passord_response(request, user)
        return Json(form.tojson()).http_response(request)

    @action
    def dismiss_message(self, request):
        app = request.app
        if not app.config['SESSION_MESSAGES']:
            raise Http404
        session = request.cache.session
        form = Form(request, data=request.body_data())
        data = form.rawdata['message']
        body = {'success': session.remove_message(data)}
        response = request.response
        response.content = json.dumps(body)
        return response


class RequirePermission(object):
    '''Decorator to apply to a view
    '''
    def __init__(self, name):
        self.name = name

    def __call__(self, router):
        router.response_wrapper = self.check_permissions
        return router

    def check_permissions(self, callable, request):
        backend = request.cache.auth_backend
        if backend.has_permission(request, self.name):
            return callable(request)
        else:
            raise PermissionDenied
