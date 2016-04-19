"""Views for managing user-related actions on a REST api server

* login
* logout
* signup
* reset_password

This user actions are served under the "authorizations" url unless
the model is overwritten.
"""
from pulsar import MethodNotAllowed, Http404

from lux.core import route, JsonRouter

from ..models import RestModel
from . import actions, api, forms


class SignUp(JsonRouter):
    """Add endpoints for signup and signup confirmation
    """
    create_user_form = forms.CreateUserForm

    def post(self, request):
        """Handle signup post data
        """
        return actions.signup(request, self.create_user_form)

    @route('<key>', method=('post', 'options'))
    def signup_confirmation(self, request):
        if not self.create_user_form:
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        backend = request.cache.auth_backend
        data = backend.signup_confirm(request, request.urlargs['key'])
        return self.json(request, data)


class ResetPassword(JsonRouter):
    reset_password_request_form = forms.EmailForm
    reset_form = forms.ChangePasswordForm

    def post(self, request):
        return actions.reset_password_request(
            request, self.reset_password_request_form)

    @route('<key>', method=('post', 'options'))
    def reset(self, request):
        #
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        key = request.urlargs['key']
        backend = request.cache.auth_backend
        user = backend.get_user(request, auth_key=key)

        if not user:
            raise Http404

        return actions.reset_password(request, self.reset_form, key)


class Authorization(api.RestRouter):
    """Authentication views for Restful APIs
    """
    model = RestModel('authorization')
    login_form = forms.LoginForm
    change_password_form = forms.ChangePasswordForm
    request_reset_password_form = forms.EmailForm

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_child(ResetPassword('reset-password'))
        self.add_child(SignUp('signup'))

    def head(self, request):
        return request.response

    def post(self, request):
        """Post request create a new Authorization token
        """
        return actions.login(request, self.login_form)

    @route('logout', metrhod=('post', 'options'))
    def logout(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        return actions.logout(request)

    @route('change-password', method=('post', 'options'))
    def change_password(self, request):
        """Change user password
        """
        # Set change_password_form to None to remove support
        # for password change
        if not self.change_password_form:
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

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

    @route('keys/<key>', method=('head', 'options'))
    def key(self, request):
        """Head method for checking if a given authorization key exists
        """
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['HEAD'])
            return request.response

        key = request.urlargs['key']
        backend = request.cache.auth_backend

        if backend.confirm_auth_key(request, key):
            return request.response
        else:
            raise Http404
