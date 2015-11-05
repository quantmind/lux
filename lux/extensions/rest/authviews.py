'''Views for managing user-related actions such as

* login
* logout
* signup
* reset_password

This user actions are served under the "authorizations" url unless
the model is overwritten.
'''
import json

from pulsar import MethodNotAllowed, Http404
from pulsar.apps.wsgi import Json

from lux import route
from lux.forms import Form

from .models import RestModel
from .views import RestRouter
from .user import AuthenticationError
from .forms import LoginForm, EmailForm, CreateUserForm, ChangePasswordForm


__all__ = ['Authorization']


def action(f):
    f.is_action = True
    return f


class ResetPasswordMixin:
    request_reset_password_form = EmailForm

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
        return Json(result).http_response(request)

    @route('reset-password/<key>', method=('post', 'options'))
    def reset(self, request):
        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request, methods=['POST'])
            return request.response

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
                fclass = self.get_fclass(self.reset_form)
                form = fclass(request, data=request.body_data())
                if form.is_valid():
                    auth = request.cache.auth_backend
                    password = form.cleaned_data['password']
                    auth.set_password(request, user, password)
                    session.info('Password successfully changed')
                    auth.auth_key_used(key)
                else:
                    result = form.tojson()
        return Json(result).http_response(request)


class LoginLogoutMixin:
    login_form = LoginForm

    @action
    def login(self, request):
        # make sure csrf is called
        form = self.login_form(request, data=request.body_data())

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

    @action
    def logout(self, request):
        # make sure csrf is called
        form = Form(request, data=request.body_data() or {})

        if form.is_valid():
            user = request.cache.user
            auth_backend = request.cache.auth_backend
            return auth_backend.logout_response(request, user)
        else:
            return Json(form.tojson()).http_response(request)


class Authorization(RestRouter,
                    LoginLogoutMixin,
                    ResetPasswordMixin):
    '''Authentication views.
    '''
    _model = RestModel('authorization')
    create_user_form = CreateUserForm
    change_password_form = ChangePasswordForm
    request_reset_password_form = EmailForm

    def head(self, request):
        return request.response

    @route('/<action>', method=('post', 'options'))
    def auth_action(self, request):
        '''Post actions
        '''
        action = request.urlargs['action'].replace('-', '_')
        method = getattr(self, action, None)
        if not getattr(method, 'is_action', False):
            raise Http404

        if request.method == 'OPTIONS':
            request.app.fire('on_preflight', request)
            return request.response

        return method(request)

    @action
    def signup(self, request):
        '''Handle signup post data

        If :attr:`.create_user_form` form is None, raise a 404 error.

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

    @action
    def change_password(self, request):
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
            auth_backend.set_password(request, user, password)
            return auth_backend.password_changed_response(request, user)
        return Json(form.tojson()).http_response(request)

    @action
    def dismiss_message(self, request):
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
