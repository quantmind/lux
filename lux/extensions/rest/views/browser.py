"""HTML views for authenticating users

These views are used by the browser authentication backends
"""
from pulsar import Http404, HttpRedirect
from pulsar.apps.wsgi import route

from lux.core import Router
from lux.forms import WebFormRouter, Layout, Fieldset, Submit

from . import forms, actions


class Login(WebFormRouter):
    """Web login view with post handler
    """
    default_form = Layout(forms.LoginForm,
                          Fieldset(all=True),
                          Submit('Login', disabled="form.$invalid"),
                          model='login',
                          showLabels=False,
                          resultHandler='login')

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    def post(self, request):
        return actions.login(request, self.fclass)


class Logout(Router):
    response_content_types = ['application/json']

    def post(self, request):
        return actions.logout(request)


class SignUp(WebFormRouter):
    """Display a signup form anf handle signup
    """
    default_form = Layout(forms.CreateUserForm,
                          Fieldset('username', 'email', 'password',
                                   'password_repeat'),
                          Submit('Sign up',
                                 disabled="form.$invalid"),
                          showLabels=False,
                          directive='user-form',
                          resultHandler='signUp')

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    def post(self, request):
        return actions.signup(request, self.fclass)

    @route('<key>')
    def confirmation(self, request):
        backend = request.cache.auth_backend
        backend.signup_confirm(request, request.urlargs['key'])
        return self.html_response(request, '')

    @route('confirmation/<username>')
    def new_confirmation(self, request):
        backend = request.cache.auth_backend
        backend.signup_confirmation(request, request.urlargs['username'])
        return self.html_response(request, '')


class ForgotPassword(WebFormRouter):
    """Manage forget passwords routes
    """
    default_form = Layout(forms.EmailForm,
                          Fieldset(all=True),
                          Submit('Submit'),
                          showLabels=False,
                          resultHandler='passwordRecovery')

    reset_form = Layout(forms.ChangePasswordForm,
                        Fieldset(all=True),
                        Submit('Change Password'),
                        showLabels=False,
                        resultHandler='passwordChanged')

    def post(self, request):
        return actions.reset_password_request(request, self.fclass)

    @route('<key>', method=('get', 'post'))
    def reset(self, request):
        """Get reste form and rest password
        """
        key = request.urlargs['key']
        backend = request.cache.auth_backend

        if not backend.confirm_auth_key(request, key):
            raise Http404

        if request.method == 'GET':
            form = self.reset_form(request)
            html = form.as_form(action=request.full_path(),
                                enctype='multipart/form-data',
                                method='post')
            return self.html_response(request, html)

        else:
            fclass = self.get_fclass(self.reset_form)
            return actions.reset_password(request, fclass, key)


class ComingSoon(WebFormRouter):
    default_form = Layout(forms.EmailForm,
                          Fieldset(all=True),
                          Submit('Get notified'),
                          showLabels=False)
