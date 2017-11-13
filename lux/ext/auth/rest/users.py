from lux.ext.rest import RestRouter, route
from lux.models import Schema, fields

from .user import UserModel, UserSchema, UserUpdateSchema, UserQuerySchema


class UserPathSchema(Schema):
    id = fields.String(description='user unique ID or username')


class UserCRUD(RestRouter):
    """
    ---
    summary: CRUD operations for users
    tags:
        - user
    """
    model = UserModel("users", UserSchema)

    @route(query_schema=UserQuerySchema,
           default_response_schema=[UserSchema],
           responses=(401, 403))
    def get(self, request, **kwargs):
        """
        ---
        summary: List users
        responses:
            200:
                description: List of users matching filters
        """
        return self.model.get_list_response(request, **kwargs)

    @route(body_schema=UserSchema,
           default_response=201,
           default_response_schema=UserSchema,
           responses=(400, 401, 403))
    def post(self, request, body_schema):
        """
        ---
        summary: Create a new user
        """
        return self.model.create_response(request, body_schema)

    @route(UserPathSchema,
           default_response_schema=UserSchema,
           responses=(401, 403))
    def get_user(self, request):
        """
        ---
        summary: Get a user by its id or username
        responses:
            200:
                description: The user matching the id or username
        """
        return self.model.get_model_response(request)

    @route(UserPathSchema,
           body_schema=UserUpdateSchema,
           default_response_schema=UserSchema,
           responses=(400, 401, 403))
    def patch_user(self, request, body_schema):
        """
        ---
        summary: Update a user by its id or username
        responses:
            201:
                description: The updated user
        """
        return self.model.update_one_response(request, body_schema)
