import json

import lux
from lux import route
from lux.forms import Form, WebFormRouter, Layout, Fieldset, Submit

from pulsar import Http404, PermissionDenied, HttpRedirect, MethodNotAllowed
from pulsar.apps.wsgi import Json

from .forms import (LoginForm, CreateUserForm, ChangePasswordForm,
                    EmailForm, PasswordForm)
from .user import AuthenticationError
from .models import RestModel


REST_CONTENT_TYPES = ['application/json']


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
        return {'columns': self.model.columns(app),
                'default-limit': app.config['API_LIMIT_DEFAULT']}

    def serialise_model(self, request, data, in_list=False):
        '''Serialise on model
        '''
        return self.model.tojson(request, data)

    def json(self, request, data):
        '''Return a response as application/json
        '''
        return Json(data).http_response(request)


class Authorization(RestRouter):
    '''Authentication views for

    * login
    * logout
    * signup
    * password change
    * password recovery

    All views respond to POST requests
    '''
    model = RestModel('authorization', LoginForm)
    create_user_form = CreateUserForm
    change_password_form = ChangePasswordForm

    def post(self, request):
        '''Anthenticate the user and create a new Authorization token
        if succesful
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed

        form = self.model.form(request, data=request.body_data())

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

    @route()
    def post_logout(self, request):
        '''Logout via post method
        '''
        # make sure csrf is called
        Form(request, data=request.body_data())

        user = request.cache.user
        if not user.is_authenticated():
            raise MethodNotAllowed

        auth_backend = request.cache.auth_backend
        return auth_backend.logout_response(request, user)

    @route()
    def post_signup(self, request):
        '''Handle signup post data

        If :attr:`.create_user_form` form is None, raise a 4040 error.

        A succesful response is returned by the backend
        :meth:`.signup_response` method.
        '''
        if not self.create_user_form:
            raise Http404

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

    @route()
    def post_change_password(self, request):
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

    def post_dismiss_message(self, request):
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


class Login(WebFormRouter):
    '''Adds login get ("text/html") and post handlers
    '''
    template = 'login.html'
    default_form = Layout(LoginForm,
                          Fieldset(all=True),
                          Submit('Login', disabled="form.$invalid"),
                          showLabels=False)

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)


class SignUp(WebFormRouter):
    template = 'signup.html'
    default_form = Layout(CreateUserForm,
                          Fieldset('username', 'email', 'password',
                                   'password_repeat'),
                          Submit('Sign up',
                                 classes='btn btn-primary btn-block',
                                 disabled="form.$invalid"),
                          showLabels=False,
                          directive='user-form')

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    @route('confirmation/<username>')
    def new_confirmation(self, request):
        username = request.urlargs['username']
        backend = request.cache.auth_backend
        backend.confirm_registration(request, username=username)
        raise HttpRedirect(self.redirect_url(request))

    @route('<key>')
    def confirmation(self, request):
        key = request.urlargs['key']
        backend = request.cache.auth_backend
        backend.confirm_registration(request, key)
        raise HttpRedirect(self.redirect_url(request))


class ChangePassword(WebFormRouter):
    default_form = Layout(ChangePasswordForm,
                          Fieldset('old_password', 'password',
                                   'password_repeat'),
                          Submit('Update password'),
                          showLabels=False)


class ForgotPassword(WebFormRouter):
    '''Adds login get ("text/html") and post handlers
    '''
    default_form = Layout(EmailForm,
                          Fieldset(all=True),
                          Submit('Submit'),
                          showLabels=False)

    template = 'forgot.html'
    reset_template = 'reset_password.html'

    def post(self, request):
        '''Handle request for resetting password
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        form = self.fclass(request, data=request.body_data())
        if form.is_valid():
            auth = request.cache.auth_backend
            email = form.cleaned_data['email']
            try:
                auth.password_recovery(request, email)
            except AuthenticationError as e:
                form.add_error_message(str(e))
            else:
                return self.maybe_redirect_to(request, form, user=user)
        return Json(form.tojson()).http_response(request)

    @route('<key>')
    def get_reset_form(self, request):
        key = request.urlargs['key']
        try:
            user = request.cache.auth_backend.get_user(request, auth_key=key)
        except AuthenticationError as e:
            session = request.cache.session
            session.error('The link is no longer valid, %s' % e)
            return request.redirect('/')
        if not user:
            raise Http404
        form = PasswordForm(request).layout
        html = form.as_form(action=request.full_path('reset'),
                            enctype='multipart/form-data',
                            method='post')
        context = {'form': html.render(request),
                   'site_name': request.config['APP_NAME']}
        return request.app.render_template(self.reset_template, context,
                                           request=request)

    @route('<key>/reset', method='post',
           response_content_types=lux.JSON_CONTENT_TYPES)
    def reset(self, request):
        key = request.urlargs['key']
        session = request.cache.session
        result = {}
        try:
            user = request.cache.auth_backend.get_user(request, auth_key=key)
        except AuthenticationError as e:
            session.error('The link is no longer valid, %s' % e)
        else:
            if not user:
                session.error('Could not find the user')
            else:
                form = PasswordForm(request, data=request.body_data())
                if form.is_valid():
                    auth = request.cache.auth_backend
                    password = form.cleaned_data['password']
                    auth.set_password(user, password)
                    session.info('Password successfully changed')
                    auth.auth_key_used(key)
                else:
                    result = form.tojson()
        return Json(result).http_response(request)


class ComingSoon(WebFormRouter):
    template = 'comingsoon.html'
    default_form = EmailForm
    redirect_to = '/'

    def post(self, request):
        '''Handle login post data
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        data = request.body_data()
        form = self.fclass(request, data=data)
        if form.is_valid():
            data = form.cleaned_data
            auth_backend = request.cache.auth_backend
            try:
                user = auth_backend.create_user(request, **data)
            except AuthenticationError as e:
                form.add_error_message(str(e))
            else:
                return self.maybe_redirect_to(request, form, user=user)
        return Json(form.tojson()).http_response(request)


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
