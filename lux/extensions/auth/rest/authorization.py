from pulsar import Http401, BadRequest
from lux.extensions.rest import RestRouter

from . import RestModel, auth_form


class Authorization(RestRouter):
    """Authentication views for Restful APIs
    """
    model = RestModel(
        'registration',
        url='authorization',
        exclude=('user_id',)
    )

    def head(self, request):
        if not request.cache.token:
            raise Http401
        return request.response

    def post(self, request):
        """Perform a login operation. The headers must contain a valid
        ``AUTHORIZATION`` token, signed by the application sending the request
        """
        if request.cache.user.is_authenticated():
            raise BadRequest

        form = auth_form(request, 'login')

        if form.is_valid():
            model = self.get_model(request)
            auth_backend = request.cache.auth_backend
            token = auth_backend.authenticate(request, **form.cleaned_data)
            data = model.tojson(request, token)
        else:
            data = form.tojson()
        return self.json_response(request, data)

    post.form = 'login'

    def delete(self, request):
        """Delete the current User Token
        """
        if not request.cache.user.is_authenticated():
            if not request.cache.token:
                raise Http401
            raise BadRequest
        model = request.app.models.token
        model.delete_model(request, request.cache.token)
        request.response.status_code = 204
        return request.response
