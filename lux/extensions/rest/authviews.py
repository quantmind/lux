"""Views for managing user-related actions:

* POST authorizations
* logout
* signup
* reset_password

This user actions are served under the "authorizations" url unless
the model is overwritten.
"""
from pulsar import MethodNotAllowed, Http404, HttpException

from lux import route

from .models import RestModel
from .views import RestRouter
from .user import AuthenticationError, login, logout
from .forms import LoginForm, EmailForm, CreateUserForm, ChangePasswordForm


__all__ = ['Authorization']


class HttpGone(HttpException):
    status = 410


def action(f):
    f.is_action = True
    return f


class SignUpMixin:
    """Add endpoints for signup and signup confirmation
    """
    create_user_form = CreateUserForm

    @action
    def signup(self, request):
        """Handle signup post data

        If :attr:`.create_user_form` form is None, raise a 404 error.

        A succesful response is returned by the backend
        :meth:`.signup_response` method.
        """
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
                email = auth_backend.signup_response(request, user)
                request.response.status_code = 201
                data = dict(email=email)
            except AuthenticationError as e:
                form.add_error_message(str(e))
                data = form.tojson()
        else:
            data = form.tojson()
        return self.json(request, data)

    @route('/signup/<key>', method=('post', 'options'))
    def signup_confirmation(self, request):
        if not self.create_user_form:
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        key = request.urlargs['key']
        backend = request.cache.auth_backend
        try:
            user = backend.get_user(request, auth_key=key)
            if user and backend.confirm_auth_key(request, key, confirm=True):
                data = dict(message='Successfully confirmed registration',
                            success=True)
            else:
                raise HttpGone('The link is no longer valid')
        except AuthenticationError:
            raise Http404
        return self.json(request, data)


class ResetPasswordMixin:
    request_reset_password_form = EmailForm
    reset_form = ChangePasswordForm

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
            except AuthenticationError as e:
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
        except AuthenticationError:
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


class Authorization(RestRouter, SignUpMixin, ResetPasswordMixin):
    """Authentication views for Restful APIs
    """
    model = RestModel('authorization')
    login_form = LoginForm
    change_password_form = ChangePasswordForm
    request_reset_password_form = EmailForm

    def head(self, request):
        return request.response

    def post(self, request):
        """Post request create a new Authorization token
        """
        return login(request, self.login_form)

    @action
    def logout(self, request):
        return logout(request)

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
