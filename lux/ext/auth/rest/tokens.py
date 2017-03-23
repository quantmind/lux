from lux.extensions.rest import CRUD, RestField
from lux.utils.auth import ensure_authenticated

from . import RestModel


class TokenModel(RestModel):
    """REST model for tokens
    """
    @classmethod
    def create(cls):
        return cls(
            'token',
            form='create-token',
            fields=[
                RestField('user', field='user_id', model='users')
            ]
        )

    def create_model(self, request, instance, data, session=None):
        user = ensure_authenticated(request)
        auth = request.cache.auth_backend
        data['session'] = False
        return auth.create_token(request, user, **data)


class TokenCRUD(CRUD):
    model = TokenModel.create()
