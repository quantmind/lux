from lux.ext.rest import RestRouter, route
from lux.models import Schema, fields

from .user import UserModel, UserSchema


class UserPathSchema(Schema):
    id = fields.String(required=True,
                       description='user unique ID or username')


class UserCRUD(RestRouter):
    """
    ---
    summary: CRUD operations for users
    """
    model = UserModel(
        "users",
        model_schema=UserSchema,
        update_schema=UserSchema
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

    @route('<id>', path_schema=UserPathSchema)
    def get_one(self, request):
        """
        ---
        summary: Get a user by its id or username
        tags:
            - user
        responses:
            200:
                description: The user matching the id or username
                schema:
                    $ref: '#/definitions/User'
        """
        return self.model.get_model_response(request)

    @route('<id>', path_schema=UserPathSchema)
    def patch_one(self, request):
        """
        ---
        summary: Update a user by its id or username
        tags:
            - user
        responses:
            200:
                description: The updated user
                schema:
                    $ref: '#/definitions/User'
        """
        return self.model.update_one_response(request)
