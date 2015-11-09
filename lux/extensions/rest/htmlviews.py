'''Base HTML views for authenticating users
'''
from pulsar import Http404, HttpRedirect, MethodNotAllowed
from pulsar.apps.wsgi import Json, route

import lux
from lux.forms import WebFormRouter, Layout, Fieldset, Submit

from .user import AuthenticationError, login, logout
from .forms import LoginForm, PasswordForm, EmailForm


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

    def post(self, request):
        return login(request, self.default_form.form_class)


class Logout(lux.Router):

    def post(self, request):
        return logout(request)


class SignUp(WebFormRouter):
    '''Display a signup form
    '''
    template = 'signup.html'

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


class ForgotPassword(WebFormRouter):
    '''Manage forget passwords routes
    '''
    default_form = Layout(EmailForm,
                          Fieldset(all=True),
                          Submit('Submit'),
                          showLabels=False,
                          resultHandler='passwordRecovery')

    reset_form = Layout(PasswordForm,
                        Fieldset(all=True),
                        Submit('Change Password'),
                        showLabels=False,
                        resultHandler='passwordChanged')

    template = 'forgot.html'
    reset_template = 'reset_password.html'

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
        form = self.reset_form(request)
        if self.form_action:
            action = self.form_action.copy()
            action['path'] = '%s/%s' % (action['path'], key)
        else:
            action = request.full_path()
        html = form.as_form(action=action,
                            enctype='multipart/form-data',
                            method='post')
        return self.html_response(request, html, self.reset_template)


class ComingSoon(WebFormRouter):
    release = 'release'
    template = 'comingsoon.html'
    default_form = Layout(EmailForm,
                          Fieldset(all=True),
                          Submit('Submit'),
                          showLabels=False,
                          resultHandler='reload')

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
                auth_backend.add_to_mail_list(request, self.release, **data)
            except AuthenticationError as e:
                form.add_error_message(str(e))
        return Json(form.tojson()).http_response(request)
