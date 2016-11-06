"""HTML views for authenticating users

These views are used by the browser authentication backends
"""
from pulsar import (
    Http404, HttpRedirect,
    PermissionDenied, MethodNotAllowed
)
from pulsar.apps.wsgi import route

from lux.core import JsonRouter
from lux.forms import (
    Form, WebFormRouter, get_form_layout, get_form_class,
    form_http_exception
)


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
                auth_backend.login(request, **form.cleaned_data)
                result = {'success': True}
            except Exception as exc:
                result = form_http_exception(form, exc)
        else:
            result = form.tojson()

        return self.json_response(request, result)


class Logout(JsonRouter):

    def post(self, request):
        form = Form(request, data=request.body_data() or {})

        if form.is_valid():
            request.cache.auth_backend.logout(request)
            result = {'success': True}
        else:
            result = form.tojson()
        return self.json_response(request, result)


class Token(JsonRouter):

    def post(self, request):
        user = request.cache.user
        if not user.is_authenticated():
            raise PermissionDenied
        form = Form(request, data=request.body_data() or {})
        if form.is_valid():
            data = {'token': request.cache.session.token}
        else:
            data = form.tojson()

        return self.json_response(request, data)


class SignUp(WebFormRouter):
    form = 'signup'

    def get(self, request):
        if request.cache.user.is_authenticated():
            raise HttpRedirect('/')
        return super().get(request)

    def post(self, request):
        form = _auth_form(request, 'signup')
        if form.is_valid():
            try:
                result = request.api.registrations.post(
                    json=form.cleaned_data,
                    jwt=True
                ).json()
                result = {'email': result['user']['email']}
                request.response.status_code = 201
            except Exception as exc:
                result = form_http_exception(form, exc)
        else:
            result = form.tojson()
        return self.json_response(request, result)

    @route('<key>')
    def confirmation(self, request):
        key = request.urlargs['key']
        request.api.registrations.post(key, jwt=True)
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
        form = _auth_form(request, 'password-recovery')
        if form.is_valid():
            try:
                result = request.api.passwords.post(
                    json=form.cleaned_data,
                    jwt=True
                ).json()
            except Exception as exc:
                result = form_http_exception(form, exc)
        else:
            result = form.tojson()
        return self.json_response(request, result)

    @route('<key>', method=('get', 'post'))
    def reset(self, request):
        """Get reset form and handle rest password
        """
        key = request.urlargs['key']

        if request.method == 'GET':
            form = get_form_layout(request, 'reset-password')
            if not form:
                raise Http404
            request.api.passwords.head(key, jwt=True)
            html = form(request).as_form(action=request.full_path(),
                                         enctype='multipart/form-data',
                                         method='post')
            return self.html_response(request, html)

        else:
            form = _auth_form(request, 'reset-password')
            if form.is_valid():
                try:
                    result = request.api.passwords.post(
                        key,
                        json=form.cleaned_data,
                        jwt=True
                    ).json()
                except Exception as exc:
                    result = form_http_exception(form, exc)
            else:
                result = form.tojson()
            return self.json_response(request, result)


def _auth_form(request, form):
    form = get_form_class(request, form)
    if not form:
        raise Http404

    request.set_response_content_type(['application/json'])
    user = request.cache.user
    if user.is_authenticated():
        raise MethodNotAllowed

    return form(request, data=request.body_data())
