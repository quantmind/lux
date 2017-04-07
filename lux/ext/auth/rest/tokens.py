from lux.models import Schema, fields
from lux.ext.rest import RestRouter
from lux.ext.odm import Model


class TokenSchema(Schema):
    user = fields.Nested('UserSchema')

    class Meta:
        model = 'tokens'


class NewTokenSchema(Schema):
    """Create a new Authorization ``Token`` for the authenticated ``User``.
    """
    description = fields.String(required=True, minLength=2, maxLength=256,
                                html_type='textarea')


class TokenCRUD(RestRouter):
    model = Model(
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
                description: A new token was succesfully created
                items:
                    $ref: '#/definitions/Token'
        """
        return self.model.create_response(request)
