from pulsar import Http404, HttpRedirect, MethodNotAllowed
from pulsar.utils.structures import AttributeDictionary
from pulsar.apps.wsgi import Json, route

import lux
from lux.forms import WebFormRouter, Layout, Fieldset, Submit
from lux.extensions.rest import (UserMixin, SessionMixin, ProcessLoginMixin,
                                 AuthenticationError, logout)
from lux.extensions.rest.forms import (LoginForm, CreateUserForm,
                                       PasswordForm, ChangePasswordForm,
                                       EmailForm)


class User(AttributeDictionary, UserMixin):
    '''A dictionary-based user

    Used by the :class:`.ApiSessionBackend`
    '''
    def is_superuser(self):
        return self.superuser

    def is_active(self):
        return True

    def __str__(self):
        return self.username or self.email or 'user'


class Session(AttributeDictionary, SessionMixin):
    '''A dictionary-based Session

    Used by the :class:`.ApiSessionBackend`
    '''
    pass


class Login(WebFormRouter):
    '''Adds login get ("text/html") and post handlers
    '''
    template = 'login.html'
    default_form = Layout(LoginForm,
                          Fieldset(all=True),
                          Submit('Login', disabled="form.$invalid"),
                          showLabels=False,
                          resultHandler='login')

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)


class LoginPost(Login, ProcessLoginMixin):
    '''Login Router for both get and post methods
    '''


class Logout(lux.Router):

    def post(self, request):
        return logout(request)


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
                          Fieldset('old_password',
                                   'password',
                                   'password_repeat'),
                          Submit('Update password'),
                          showLabels=False,
                          resultHandler='reload')


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
    default_form = Layout(EmailForm,
                          Fieldset(all=True),
                          Submit('Submit'),
                          showLabels=False,
                          resultHandler='reload')
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
