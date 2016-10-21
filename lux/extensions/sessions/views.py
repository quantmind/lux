"""HTML views for authenticating users

These views are used by the browser authentication backends
"""
from pulsar import Http404, HttpRedirect, UnprocessableEntity
from pulsar.apps.wsgi import route

from lux.core import Router, AuthenticationError
from lux.forms import WebFormRouter, get_form_layout, get_form_class

from . import actions


class Login(WebFormRouter):
    """Web login view with post handler
    """
    form = 'login'

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    def post(self, request):
        form = _auth_form(request, 'login')

        if form.is_valid():
            auth_backend = request.cache.auth_backend
            try:
                user = auth_backend.authenticate(request, **form.cleaned_data)
                if not user.is_anonymous():
                    result = auth_backend.login(request, user)
                else:
                    raise AuthenticationError('Cannot login')
            except AuthenticationError as exc:
                raise UnprocessableEntity(str(exc)) from None
        else:
            result = form.tojson()

        return self.json_response(request, result)


class Logout(Router):
    form_enctype = 'application/json'
    response_content_types = ['application/json']

    def post(self, request):
        return actions.logout(request)


class SignUp(WebFormRouter):
    """Display a signup form anf handle signup
    """
    form = 'signup'

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    def post(self, request):
        return actions.signup(request)

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
    form = 'password-recovery'

    def post(self, request):
        return actions.reset_password_request(request)

    @route('<key>', method=('get', 'post'))
    def reset(self, request):
        """Get reset form and handle rest password
        """
        key = request.urlargs['key']
        backend = request.cache.auth_backend

        if not backend.confirm_auth_key(request, key):
            raise Http404

        if request.method == 'GET':
            form = get_form_layout(request, 'reset-password')
            if not form:
                raise Http404
            html = form(request).as_form(action=request.full_path(),
                                         enctype='multipart/form-data',
                                         method='post')
            return self.html_response(request, html)

        else:
            return actions.reset_password(request, key)


def _auth_form(request, form):
    form = get_form_class(request, form)
    if not form:
        raise Http404

    request.set_response_content_type(['application/json'])
    user = request.cache.user
    if user.is_authenticated():
        raise MethodNotAllowed

    return form(request, data=request.body_data())
