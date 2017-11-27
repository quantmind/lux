from datetime import datetime

from lux.models import Schema, fields
from lux.ext.rest import RestRouter, route
from lux.ext.odm import Model


class TokenSchema(Schema):
    user = fields.Nested('UserSchema')

    class Meta:
        model = 'tokens'


class TokenCreateSchema(TokenSchema):
    """Create a new Authorization ``Token`` for the authenticated ``User``.
    """
    description = fields.String(required=True, minLength=2, maxLength=256)


class TokenModel(Model):

    def get_one(self, session, *filters, **kwargs):
        query = self.query(session, *filters, **kwargs)
        token = query.one()
        query.update({'last_access': datetime.utcnow()},
                     synchronize_session=False)
        return token


class TokenCRUD(RestRouter):
    """
    ---
    summary: Mange user tokens
    tags:
        - user
        - token
    """
    model = TokenModel('tokens', TokenSchema)

    @route(default_response_schema=[TokenSchema])
    def get(self, request):
        """
        ---
        summary: List tokens for a user
        responses:
            200:
                description: List all user tokens matching query filters
        """
        return self.model.get_list_response(request)

    @route(default_response=201,
           default_response_schema=TokenSchema,
           body_schema=TokenCreateSchema)
    def post(self, request):
        """
        ---
        summary: Create a new token
        """
        return self.model.create_response(request)
