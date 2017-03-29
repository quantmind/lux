from pulsar.api import Http401, BadRequest

from lux.core import AuthenticationError
from lux.models import Schema, fields, validators
from lux.utils.date import date_from_now
from lux.ext.rest import RestRouter, RestModel

from . import auth_form, ensure_service_user


class LoginSchema(Schema):
    """The Standard login schema
    """
    error_message = 'Incorrect username or password'
    username = fields.Slug(
        required=True,
        minLength=2,
        maxLength=30,
        validate=validators.string
    )
    password = fields.Password(
        required=True,
        minLength=2,
        maxLength=128,
        validate=validators.string
    )


class AuthorizeSchema(LoginSchema):
    expiry = fields.DateTime()
    user_agent = fields.String()
    ip_address = fields.String()


class Authorization(RestRouter):
    """Authentication views for Restful APIs
    """
    model = RestModel(
        'authorizations',
        post_form=AuthorizeSchema,
        url='authorizations',
        exclude=('user_id',)
    )

    def head(self, request):
        """
        summary: Check token validity
        description: Check validity of the token in the
            Authorization header. It works for both user and
            application tokens.

        responses:
            200:
                Token is valid
            400:
                Bad Token
            401:
                Token is expired or not available
        """
        if not request.cache.token:
            raise Http401
        return request.response

    def post(self, request):
        """
        summary: Perform a login operation
        description: The headers must contain a valid token
            signed by the application sending the request

        responses:
            201:
                description: Successful response
                schema:
                    $ref: '#/definitions/Token'
            400:
                description: Bad Application Token
                schema:
                    $ref: '#/definitions/ErrorMessage'
            401:
                description: Application Token is expired or not available
                schema:
                    $ref: '#/definitions/ErrorMessage'
            403:
                description: The Application has no permission to login users
                schema:
                    $ref: '#/definitions/ErrorMessage'
            422:
                description: The login payload did not validate
                schema:
                    $ref: '#/definitions/ErrorMessage'
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

    def delete(self, request):
        """
        summary: Delete the token used by the authenticated User
        description: A valid bearer token must be available in the
            Authorization header

        responses:
            204:
                description: Token was successfully deleted
            400:
                description: Bad User Token
                schema:
                    $ref: '#/definitions/ErrorMessage'
            401:
                description: User Token is expired or not available
                schema:
                    $ref: '#/definitions/ErrorMessage'
        """
        if not request.cache.user.is_authenticated():
            if not request.cache.token:
                raise Http401('Token')
            raise BadRequest
        model = request.app.models['tokens']
        model.delete_model(request, request.cache.token)
        request.response.status_code = 204
        return request.response
