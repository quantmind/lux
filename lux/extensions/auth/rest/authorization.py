from datetime import datetime, timedelta

from pulsar import Http401, BadRequest
from lux.extensions.rest import RestRouter

from . import RestModel, auth_form


class Authorization(RestRouter):
    """Authentication views for Restful APIs
    """
    model = RestModel(
        'token',
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
        # user must be anonymous
        if not request.cache.user.is_anonymous():
            raise BadRequest
        # the service user must be authenticated
        if not request.cache.user.is_authenticated():
            raise Http401('Token')

        form = auth_form(request, 'login')

        if form.is_valid():
            model = self.get_model(request)
            auth_backend = request.cache.auth_backend
            data = form.cleaned_data
            max_expiry = request.config['MAX_TOKEN_SESSION_EXPIRY']
            expiry = max(data.pop('expiry', None) or 0, 0)
            expiry = min(expiry, max_expiry) or max_expiry
            expiry = datetime.utcnow() + timedelta(seconds=expiry)
            user = auth_backend.authenticate(request, **data)
            token = auth_backend.create_token(request, user, expiry=expiry,
                                              session=True)
            request.response.status_code = 201
            data = model.tojson(request, token)
        else:
            data = form.tojson()
        return self.json_response(request, data)

    post.form = 'login'
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
                raise Http401
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
