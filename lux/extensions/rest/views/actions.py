"""Backend actions"""
from pulsar.apps.wsgi import Json
from pulsar.utils.slugify import slugify
from pulsar import HttpException, Http404, MethodNotAllowed

from lux.core import json_message
from lux.forms import Form, ValidationError


class AuthenticationError(ValueError):
    pass


def login(request, fclass):
    """Authenticate the user
    """
    form = _login_form(request, fclass)

    if form.is_valid():
        auth_backend = request.cache.auth_backend
        try:
            user = auth_backend.authenticate(request, **form.cleaned_data)
            if user.is_active():
                result = auth_backend.login(request, user)
                return Json(result).http_response(request)
            else:
                return auth_backend.inactive_user_login_response(request,
                                                                 user)
        except AuthenticationError as exc:
            raise HttpException(str(exc), 422) from exc

    return Json(form.tojson()).http_response(request)


def signup(request, form):
    """Signup a user
    """
    form = _login_form(request, form)

    if form.is_valid():
        auth_backend = request.cache.auth_backend
        try:
            data = auth_backend.signup(request, **form.cleaned_data)
            request.response.status_code = 201
        except (AuthenticationError, ValidationError) as exc:
            form.add_error_message(str(exc))
            data = form.tojson()
    else:
        data = form.tojson()

    return Json(data).http_response(request)


def logout(request):
    '''Logout a user
    '''
    form = Form(request, data=request.body_data() or {})

    if form.is_valid():
        request.cache.auth_backend.logout(request)
        return Json({'success': True}).http_response(request)
    else:
        return Json(form.tojson()).http_response(request)


def check_username(request, username):
    correct = slugify(username)
    if correct != username:
        raise ValidationError('Username may only contain lowercase '
                              'alphanumeric characters or single hyphens, '
                              'and cannot begin or end with a hyphen')
    return username


def user_permissions(request):
    """Return a dictionary of permissions for the current user

    :request: a WSGI request with url data ``resource`` and ``action``.
    """
    backend = request.cache.auth_backend
    resources = request.url_data.get('resource', ())
    actions = request.url_data.get('action')
    return backend.get_permissions(request, resources, actions=actions)


def reset_password_request(request, fclass):
    """Request a reset password code/email
    """
    form = _login_form(request, fclass)
    if form.is_valid():
        auth = request.cache.auth_backend
        email = form.cleaned_data['email']
        try:
            data = auth.password_recovery(request, email=email)
        except AuthenticationError as e:
            data = json_message(request, str(e), error=True)
    else:
        data = form.tojson()
    return Json(data).http_response(request)


def reset_password(request, fclass, key):
    """Reset password
    """
    form = _login_form(request, fclass)
    if form.is_valid():
        auth = request.cache.auth_backend
        password = form.cleaned_data['password']
        try:
            data = auth.set_password(request, password, auth_key=key)
        except AuthenticationError as e:
            data = json_message(request, str(e), error=True)
    else:
        data = form.tojson()
    return Json(data).http_response(request)


def _login_form(request, form):
    if not form:
        raise Http404

    request.set_response_content_type(['application/json'])
    user = request.cache.user
    if user.is_authenticated():
        raise MethodNotAllowed

    return form(request, data=request.body_data())
