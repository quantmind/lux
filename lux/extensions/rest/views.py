import lux
from lux import route, HtmlRouter
from lux.forms import Form, WebFormRouter, FormMixin, Layout, Fieldset, Submit

from pulsar import Http404, PermissionDenied, HttpRedirect, MethodNotAllowed
from pulsar.apps.wsgi import Json, Router

from .forms import (LoginForm, CreateUserForm, ChangePasswordForm,
                    EmailForm, PasswordForm)
from .user import AuthenticationError
from .models import RestModel


REST_CONTENT_TYPES = ['application/json']


def csrf(method):
    '''Decorator which makes sure the CSRF token is checked

    This decorator should be applied to all view handling POST data
    without using a :class:`.Form`.
    '''
    def _(self, request):
        # make sure CSRF is checked
        data, files = request.data_and_files()
        Form(request, data=data, files=files)
        return method(self, request)

    return _


class RestRoot(lux.Router):
    '''Api Root'''
    response_content_types = REST_CONTENT_TYPES

    def apis(self, request):
        routes = {}
        for route in self.routes:
            routes[route.model.api_name] = request.absolute_uri(route.path())
        return routes

    def get(self, request):
        return Json(self.apis(request)).http_response(request)


class RestMixin:
    model = None
    '''Instance of a :class:`~lux.extensions.rest.RestModel`
    '''
    def __init__(self, *args, **kwargs):
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

    def serialise_model(self, request, data, in_list=False):
        '''Serialise on model
        '''
        raise NotImplementedError

    def json(self, request, data):
        '''Return a response as application/json
        '''
        return Json(data).http_response(request)


class Login(WebFormRouter):
    '''Adds login get ("text/html") and post handlers
    '''
    default_form = Layout(LoginForm,
                          Fieldset(all=True),
                          Submit('Login', disabled="form.$invalid"),
                          showLabels=False)
    template = 'login.html'
    redirect_to = '/'

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect(self.redirect_to)
        return super().get(request)

    def post(self, request):
        '''Handle login post data
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        form = self.fclass(request, data=request.body_data())
        if form.is_valid():
            auth = request.cache.auth_backend
            try:
                user = auth.authenticate(request, **form.cleaned_data)
                auth.login(request, user)
            except AuthenticationError as e:
                form.add_error_message(str(e))
            else:
                return self.maybe_redirect_to(request, form, user=user)
        return Json(form.tojson()).http_response(request)


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

    @route('confirmation/<username>')
    def new_confirmation(self, request):
        username = request.urlargs['username']
        backend = request.cache.auth_backend
        user = backend.confirm_registration(request, username=username)
        raise HttpRedirect(self.redirect_url(request))

    @route('<key>')
    def confirmation(self, request):
        key = request.urlargs['key']
        backend = request.cache.auth_backend
        user = backend.confirm_registration(request, key)
        raise HttpRedirect(self.redirect_url(request))


class ChangePassword(WebFormRouter):
    default_form = Layout(ChangePasswordForm,
                          Fieldset('old_password', 'password',
                                   'password_repeat'),
                          Submit('Update password'),
                          showLabels=False)

    def post(self, request):
        '''Handle post data
        '''
        user = request.cache.user
        form = change_password(request, self.form_class)
        if form.is_valid():
            return self.maybe_redirect_to(request, form, user=user)
        return Json(form.tojson()).http_response(request)


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


class Logout(Router, FormMixin):
    '''Logout handler, post view only
    '''
    redirect_to = '/'

    def post(self, request):
        '''Logout via post method
        '''
        # validate CSRF
        form = self.fclass(request, data=request.body_data())
        backend = request.cache.auth_backend
        backend.logout(request)
        return self.maybe_redirect_to(request, form)


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


def change_password(request, form_class):
    user = request.cache.user
    if not user.is_authenticated():
        raise MethodNotAllowed
    form = form_class(request, data=request.body_data())
    if form.is_valid():
        auth = request.cache.auth_backend
        password = form.cleaned_data['password']
        auth.set_password(user, password)
    return form
