from pulsar.api import Http401, BadRequest, UnprocessableEntity

from lux.models import Schema, fields, ValidationError
from lux.utils.date import date_from_now
from lux.ext.rest import RestRouter, route
from lux.ext.odm import Model

from ..backend import AuthenticationError
from .tokens import TokenSchema
from . import ensure_service_user


class LoginSchema(Schema):
    """The Standard login schema
    """
    username = fields.Slug(
        required=True,
        minLength=2,
        maxLength=30
    )
    password = fields.Password(
        required=True,
        minLength=2,
        maxLength=128
    )


class AuthorizeSchema(LoginSchema):
    expiry = fields.Int()
    user_agent = fields.String()
    ip_address = fields.String()

    def post_load(self, data):
        """Perform authentication by creating a session token if possible
        """
        session = self.model.object_session(data)
        maxexp = date_from_now(session.config['MAX_TOKEN_SESSION_EXPIRY'])
        data['user'] = session.auth.authenticate(session, **data)
        if not data['user']:
            raise ValidationError('Invalid username or password')
        data.pop('username')
        data.pop('password')
        data['session'] = True
        data['expiry'] = min(data.get('expiry') or maxexp, maxexp)
        # create the db token
        tokens = session.models['tokens']
        return tokens.create_one(session, data, tokens.model_schema)


class AuthorizationModel(Model):

    def data_and_files(self, request):
        data, files = super().data_and_files(request)
        maxexp = request.config['MAX_TOKEN_SESSION_EXPIRY']
        data['expiry'] = min(data.get('expiry') or maxexp, maxexp)
        data['user_agent'] = request.get('HTTP_USER_AGENT')
        return data, files

    def create_instance(self, session, data):
        try:
            data['user'] = session.auth.authenticate(
                session,
                username=data.pop('username'),
                password=data.pop('password')
            )
        except AuthenticationError as exc:
            raise UnprocessableEntity(str(exc)) from None
        if not data['user']:
            raise ValidationError('Invalid username or password')


class Authorization(RestRouter):
    """
    ---
    summary: Authentication path
    description: provide operation for creating new authentication tokens
        and check their validity
    tags:
        - authentication
    """
    model = AuthorizationModel('authorizations', TokenSchema, db_name='token')

    @route()
    def head(self, request):
        """
        ---
        summary: Check token validity
        description: Check validity of the token in the
            Authorization header. It works for both user and
            application tokens.
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

    @route(body_schema=AuthorizeSchema,
           default_response=201,
           default_response_schema=TokenSchema,
           responses=(400, 401, 403, 422))
    def post(self, request, **kw):
        """
        ---
        summary: Create a new user token
        description: The headers must contain a valid token
            signed by the application sending the request
        """
        ensure_service_user(request)
        return self.model.create_response(request, **kw)

    @route(default_response=204,
           responses=(401, 403))
    def delete(self, request):
        """
        ---
        summary: Delete the token used by the authenticated User
        description: A valid bearer token must be available in the
            Authorization header
        """
        token = request.cache.get('token')
        if not request.cache.user.is_authenticated():
            if not token:
                raise Http401
            raise BadRequest
        return self.model.delete_one_response(request, token)
