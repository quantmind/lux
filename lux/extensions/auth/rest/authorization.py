from pulsar import Http401, BadRequest

from lux import forms
from lux.core import AuthenticationError
from lux.utils.date import date_from_now
from lux.extensions.rest import RestRouter
from lux.extensions.rest.views.forms import LoginForm

from . import RestModel, auth_form, ensure_service_user


class AuthorizeForm(LoginForm):
    expiry = forms.DateTimeField(required=False)
    user_agent = forms.TextField(required=False)
    ip_address = forms.CharField(required=False)


class Authorization(RestRouter):
    """Authentication views for Restful APIs
    """
    model = RestModel(
        'token',
        form=AuthorizeForm,
        url='authorizations',
        exclude=('user_id',)
    )

    def head(self, request):
        """Check validity of the ``Token`` in the ``Authorization`` header.
        It works for both user and application tokens.
        """
        if not request.cache.token:
            raise Http401
        return request.response

    head.responses = (
        (200, "Token is valid"),
        (400, "Bad Token"),
        (401, "Token is expired or not available")
    )

    def post(self, request):
        """Perform a login operation. The headers must contain a valid
        ``AUTHORIZATION`` token, signed by the application sending the request
        """
        ensure_service_user(request)
        model = self.get_model(request)
        form = auth_form(request, model.form)

        if form.is_valid():
            model = self.get_model(request)
            auth_backend = request.cache.auth_backend
            data = form.cleaned_data
            maxexp = date_from_now(request.config['MAX_TOKEN_SESSION_EXPIRY'])
            expiry = min(data.pop('expiry', maxexp), maxexp)
            user_agent = data.pop('user_agent', None)
            ip_address = data.pop('ip_address', None)
            try:
                user = auth_backend.authenticate(request, **data)
                token = auth_backend.create_token(request, user,
                                                  expiry=expiry,
                                                  description=user_agent,
                                                  ip_address=ip_address,
                                                  session=True)
            except AuthenticationError as exc:
                form.add_error_message(str(exc))
                data = form.tojson()
            else:
                request.response.status_code = 201
                data = model.tojson(request, token)
        else:
            data = form.tojson()
        return self.json_response(request, data)

    post.responses = (
        (201, "Successful response"),
        (400, "Bad Application Token"),
        (401, "Application Token is expired or not available"),
        (403, "The Application has no permission to login users"),
        (422, "The login payload did not validate")
    )

    def delete(self, request):
        """Delete the token used by the authenticated User. A valid bearer
        token must be available in the ``Authorization`` header
        """
        if not request.cache.user.is_authenticated():
            if not request.cache.token:
                raise Http401('Token')
            raise BadRequest
        model = request.app.models['tokens']
        model.delete_model(request, request.cache.token)
        request.response.status_code = 204
        return request.response

    delete.responses = (
        (204, "Token was successfully deleted"),
        (400, "Bad User Token"),
        (401, "User Token is expired or not available")
    )
