from datetime import datetime

from lux.models import Schema, fields
from lux.ext.rest import RestRouter
from lux.ext.odm import Model


class TokenSchema(Schema):
    user = fields.Nested('UserSchema')

    class Meta:
        model = 'tokens'


class NewTokenSchema(TokenSchema):
    """Create a new Authorization ``Token`` for the authenticated ``User``.
    """
    description = fields.String(required=True, minLength=2, maxLength=256,
                                html_type='textarea')


class TokenModel(Model):

    def get_one(self, session, *filters, **kwargs):
        query = self.query(session, *filters, **kwargs)
        token = query.one()
        query.update({'last_access': datetime.utcnow()},
                     synchronize_session=False)
        return token


class TokenCRUD(RestRouter):
    model = TokenModel(
        'tokens',
        model_schema=TokenSchema,
        create_schema=NewTokenSchema
    )

    def get(self, request):
        """
        ---
        summary: List users
        tags:
            - user
        responses:
            200:
                description: List of users matching filters
                type: array
                items:
                    $ref: '#/definitions/User'
        """
        return self.model.get_list_response(request)

    def post(self, request):
        """
        ---
        summary: Create a new token
        tags:
            - user
            - token
        responses:
            201:
                description: A new token was successfully created
                schema:
                    $ref: '#/definitions/Token'
        """
        return self.model.create_response(request)
