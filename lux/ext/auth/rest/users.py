from lux.ext.rest import RestRouter, route

from .user import UserModel, UserSchema


class UserCRUD(RestRouter):
    """
    ---
    summary: CRUD operations for users
    """
    model = UserModel(
        "users",
        model_schema=UserSchema
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

    @route('<id>')
    def get_one(self, request):
        """
        ---
        summary: Get a user by its id or username
        tags:
            - user
        responses:
            200:
                description: List of users matching filters
                type: array
                items:
                    $ref: '#/definitions/User'
        """
        return self.model.get_model_response(request)

    @route('<id>')
    def patch_one(self, request):
        """
        ---
        summary: Update a user by its id or username
        tags:
            - user
        responses:
            200:
                description: List of users matching filters
                type: array
                items:
                    $ref: '#/definitions/User'
        """
        return self.model.update_model_response(request)
