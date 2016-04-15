"""Views for managing user-related actions on a REST api server

* login
* logout
* signup
* reset_password

This user actions are served under the "authorizations" url unless
the model is overwritten.
"""
from pulsar import MethodNotAllowed, Http404

from lux.core import route

from ..models import RestModel
from . import actions, api, forms


def action(f):
    f.is_action = True
    return f


class SignUpMixin:
    """Add endpoints for signup and signup confirmation
    """
    create_user_form = forms.CreateUserForm

    @action
    def signup(self, request):
        """Handle signup post data
        """
        return actions.signup(request, self.create_user_form)

    @route('/signup/<key>', method=('post', 'options'))
    def signup_confirmation(self, request):
        if not self.create_user_form:
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        backend = request.cache.auth_backend
        data = backend.signup_confirm(request, request.urlargs['key'])
        return self.json(request, data)


class ResetPasswordMixin:
    request_reset_password_form = forms.EmailForm
    reset_form = forms.ChangePasswordForm

    @action
    def reset_password(self, request):
        user = request.cache.user
        if user.is_authenticated() or not self.request_reset_password_form:
            raise MethodNotAllowed

        form = self.request_reset_password_form(request,
                                                data=request.body_data())
        if form.is_valid():
            auth = request.cache.auth_backend
            email = form.cleaned_data['email']
            try:
                result = {'email': auth.password_recovery(request, email)}
            except actions.AuthenticationError as e:
                form.add_error_message(str(e))
                result = form.tojson()
        else:
            result = form.tojson()
        return self.json(request, result)

    @route('reset-password/<key>', method=('post', 'options'))
    def reset(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        key = request.urlargs['key']
        try:
            user = request.cache.auth_backend.get_user(request, auth_key=key)
        except actions.AuthenticationError:
            user = None
        form = self.reset_form(request, data=request.body_data())
        valid = form.is_valid()
        if not user:
            form.add_error_message('The link is no longer valid')
            result = form.tojson()
        elif valid:
                auth = request.cache.auth_backend
                password = form.cleaned_data['password']
                if auth.set_password(request, user, password):
                    result = dict(message='Password successfully changed',
                                  success=True)
                else:
                    result = dict(error='Could not change password')
                auth.confirm_auth_key(request, key)
        else:
            result = form.tojson()
        return self.json(request, result)


class Authorization(api.RestRouter, SignUpMixin, ResetPasswordMixin):
    """Authentication views for Restful APIs
    """
    model = RestModel('authorization')
    login_form = forms.LoginForm
    change_password_form = forms.ChangePasswordForm
    request_reset_password_form = forms.EmailForm

    def head(self, request):
        return request.response

    def post(self, request):
        """Post request create a new Authorization token
        """
        return actions.login(request, self.login_form)

    @action
    def logout(self, request):
        return actions.logout(request)

    @route('/<action>', method=('post', 'options'))
    def auth_action(self, request):
        """Post actions
        """
        action = request.urlargs['action'].replace('-', '_')
        method = getattr(self, action, None)
        if not getattr(method, 'is_action', False):
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        return method(request)

    @action
    def change_password(self, request):
        """Change user password
        """
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
            auth_backend.set_password(request, user, password)
            result = {'success': True,
                      'message': 'password changed'}
        else:
            result = form.tojson()
        return self.json(request, result)
