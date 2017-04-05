from lux.ext.rest import RestRouter

from .user import UserModel


class UserCRUD(RestRouter):
    """
    ---
    summary: CRUD operations for users
    """
    model = UserModel(
        "users",
        model_schema='UserSchema'
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
        return self.model.get_list(request)
