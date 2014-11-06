import lux
from lux import route
from lux.forms import Form
from lux.extensions.angular import Router as WebRouter

from pulsar import Http404, PermissionDenied
from pulsar.apps.wsgi import Json

from .forms import (LoginForm, CreateUserForm, ChangePassword,
                    ForgotPasswordForm, ChangePassword2)
from .backend import AuthenticationError
from .jwtmixin import jwt


__all__ = ['Login', 'SignUp', 'Logout', 'Token', 'ForgotPassword', 'csrf']


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


class FormMixin(object):
    default_form = Form
    form = None
    redirect_to = None

    @property
    def fclass(self):
        return self.form or self.default_form

    def maybe_redirect_to(self, request, form, **kw):
        redirect_to = self.redirect_to
        if redirect_to:
            if hasattr(redirect_to, '__call__'):
                redirect_to = redirect_to(request, **kw)
        if redirect_to:
            return Json({'success': True,
                         'redirect': request.absolute_uri(redirect_to)}
                        ).http_response(request)
        else:
            Json(form.tojson()).http_response(request)


class WebFormRouter(WebRouter, FormMixin):
    template = None

    def build_main(self, request):
        '''Handle the HTML page for login
        '''
        form = self.fclass(request).layout
        html = form.as_form(action=request.full_path(),
                            enctype='multipart/form-data',
                            method='post')
        context = {'form': html.render(request)}
        return request.app.render_template(self.template, context,
                                           request=request)


class Login(WebFormRouter):
    '''Adds login get ("text/html") and post handlers
    '''
    default_form = LoginForm
    template = 'login.html'
    redirect_to = '/'

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
    default_form = CreateUserForm
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
        return request.redirect('/')

    @route('<key>')
    def confirmation(self, request):
        key = request.urlargs['key']
        backend = request.cache.auth_backend
        user = backend.confirm_registration(request, key)
        return request.redirect('/')


class ForgotPassword(WebFormRouter):
    '''Adds login get ("text/html") and post handlers
    '''
    default_form = ForgotPasswordForm
    template = 'forgot.html'

    @route('<key>')
    def get_reset_form(self, request):
        key = request.urlargs['key']
        try:
            user = request.app.auth_backend.get_user(request, auth_key=key)
        except AuthenticationError as e:
            session = request.cache.session
            session.error('The link is no longer valid, %s' % e)
            return request.redirect('/')
        if not user:
            raise Http404
        form = ChangePassword2(request)
        html = form.layout(request, action=request.full_path('reset'))
        context = {'form': html.render(request),
                   'site_name': request.config['APP_NAME']}
        return request.app.html_response(request, 'reset_password.html',
                                         context=context)

    def post(self, request):
        '''Handle request for resetting password
        '''
        user = request.cache.user
        if user.is_authenticated():
            raise MethodNotAllowed
        form = self.fclass(request, data=request.body_data())
        if form.is_valid():
            auth = request.app.auth_backend
            email = form.cleaned_data['email']
            try:
                auth.password_recovery(request, email)
            except AuthenticationError as e:
                form.add_error_message(str(e))
            else:
                return self.maybe_redirect_to(request, form, user=user)
        return Json(form.tojson()).http_response(request)

    @route('<key>/reset', method='post',
           response_content_types=lux.JSON_CONTENT_TYPES)
    def reset(self, request):
        key = request.urlargs['key']
        session = request.cache.session
        result = {}
        try:
            user = request.app.auth_backend.get_user(request, auth_key=key)
        except AuthenticationError as e:
            session.error('The link is no longer valid, %s' % e)
        else:
            if not user:
                session.error('Could not find the user')
            else:
                form = ChangePassword2(request, data=request.body_data())
                if form.is_valid():
                    auth = request.app.auth_backend
                    password = form.cleaned_data['password']
                    auth.set_password(user, password)
                    session.info('Password successfully changed')
                    auth.auth_key_used(key)
                else:
                    result = form.tojson()
        return Json(result).http_response(request)


class Logout(lux.Router, FormMixin):
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


class Token(lux.Router):

    @csrf
    def post(self, request):
        '''Obtain a Json Web Token (JWT)
        '''
        user = request.cache.user
        if not user:
            raise PermissionDenied
        cfg = request.config
        secret = cfg['SECRET_KEY']
        token = jwt.encode({'username': user.username,
                            'application': cfg['APP_NAME']}, secret)
        return Json({'token': token}).http_response(request)
