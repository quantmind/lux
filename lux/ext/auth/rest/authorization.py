from pulsar.api import Http401, BadRequest

from lux.models import Schema, fields, validators, ValidationError
from lux.utils.date import date_from_now
from lux.ext.rest import RestRouter
from lux.ext.odm import Model, object_session

from . import ensure_service_user


class LoginSchema(Schema):
    """The Standard login schema
    """
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

    def post_load(self, token):
        """Perform authentication if possible
        """
        session = object_session(token)
        token.user = self.authenticate(token)
        maxexp = date_from_now(session.config['MAX_TOKEN_SESSION_EXPIRY'])
        token.session = True
        token.expiry = min(token.expiry or maxexp, maxexp)

    def authenticate(self, token):
        raise ValidationError('Invalid username or password')

    class Meta:
        model = 'token'


class Authorization(RestRouter):
    """Authentication views for Restful APIs
    """
    model = Model(
        'authorizations',
        create_schema=AuthorizeSchema
    )

    def head(self, request):
        """
        ---
        summary: Check token validity
        description: Check validity of the token in the
            Authorization header. It works for both user and
            application tokens.
        tags:
            - auth
        responses:
            200:
                description: Token is valid
            400:
                description: Bad Token
            401:
                description: Token is expired or not available
        """
        if not request.cache.get('token'):
            raise Http401
        return request.response

    def post(self, request):
        """
        ---
        summary: Perform a login operation
        description: The headers must contain a valid token
            signed by the application sending the request
        tags:
            - auth
        responses:
            201:
                description: Successful response
                schema:
                    $ref: '#/definitions/Token'
            400:
                description: Bad Application Token or payload not valid JSON
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
        return self.create_response(request)

    def delete(self, request):
        """
        ---
        summary: Delete the token used by the authenticated User
        description: A valid bearer token must be available in the
            Authorization header
        tags:
            - auth
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
        token = request.cache.get('token')
        if not request.cache.user.is_authenticated():
            if not token:
                raise Http401
            raise BadRequest
        return self.delete_one_response(request, token)
