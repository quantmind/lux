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
from lux.forms import get_form_class

from ..models import RestModel
from . import actions, api


class SignUp(JsonRouter):
    """Add endpoints for signup and signup confirmation
    """
    def post(self, request):
        """Handle signup post data
        """
        return actions.signup(request)

    @route('<key>', method=('post', 'options'))
    def signup_confirmation(self, request):
        if not get_form_class('signup'):
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        backend = request.cache.auth_backend
        data = backend.signup_confirm(request, request.urlargs['key'])
        return self.json(request, data)


class ResetPassword(JsonRouter):

    def post(self, request):
        return actions.reset_password_request(request)

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

        return actions.reset_password(request, key)


class Authorization(api.RestRouter):
    """Authentication views for Restful APIs
    """
    model = RestModel('authorization')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_child(ResetPassword('reset-password'))
        self.add_child(SignUp('signup'))

    def head(self, request):
        return request.response

    def post(self, request):
        """Post request create a new Authorization token
        """
        return actions.login(request)

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
        fclass = get_form_class('change-password')

        if not fclass:
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

        user = request.cache.user
        if not user.is_authenticated():
            raise MethodNotAllowed

        form = fclass(request, data=request.body_data())

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
