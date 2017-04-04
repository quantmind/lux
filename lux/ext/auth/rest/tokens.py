from lux.models import Schema, fields
from lux.ext.rest import RestRouter
from lux.ext.odm import Model
from lux.utils.auth import ensure_authenticated


class TokenSchema(Schema):
    user = fields.Nested('UserSchema')


class NewTokenSchema(Schema):
    """Create a new Authorization ``Token`` for the authenticated ``User``.
    """
    description = fields.String(required=True, minLength=2, maxLength=256,
                                html_type='textarea')


class TokenModel(Model):
    """REST model for tokens
    """
    def create_model(self, request, instance, data, session=None):
        user = ensure_authenticated(request)
        auth = request.cache.auth_backend
        data['session'] = False
        return auth.create_token(request, user, **data)


class TokenCRUD(RestRouter):
    model = TokenModel(
        'tokens',
        model_schema=TokenSchema,
        create_schema=NewTokenSchema
    )
