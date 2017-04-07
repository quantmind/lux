from pulsar.api import Http401

from lux.core import route
from lux.ext.odm import Model
from lux.ext.rest import RestRouter, user_permissions
from lux.models import fields, Schema


URI = 'users'


class UserSchema(Schema):
    username = fields.Slug(required=True, readOnly=True)
    joined = fields.DateTime(readOnly=True)
    full_name = fields.String(
        field=('first_name', 'last_name', 'username', 'email'),
        readOnly=True
    )
    groups = fields.Nested('GroupSchema', multi=True)

    class Meta:
        exclude = ('password', 'superuser')
        # model = URI


class UserModel(Model):

    @property
    def authenticated(self):
        return self.metadata.get('authenticated', False)

    def get_one(self, session, *args, **kwargs):
        """When authenticated is True return the current user or
        raise Http401
        """
        if self.authenticated:
            user = session.request.cache.get('user')
            if not user.is_authenticated():
                raise Http401
            return user
        return super().get_instance(session, *args, **kwargs)


class UserRest(RestRouter):
    """
    ---
    summary: Rest operations for the authenticated user
    """
    model = UserModel(
        'user',
        model_schema=UserSchema,
        update_schema=UserSchema,
        authenticated=True
    )

    def get(self, request):
        """
        ---
        summary: get the authenticated user
        tags:
            - user
        responses:
            200:
                description: the authenticated user
                schema:
                    $ref: '#/definitions/User'
            401:
                description: not authenticated
                schema:
                    $ref: '#/definitions/ErrorMessage'

        """
        return self.model.get_one_response(request)

    def patch(self, request):
        """
        ---
        summary: Update authenticated user and/or user profile
        tags:
            - user
        responses:
            200:
                description: successfully updated
                schema:
                    $ref: '#/definitions/User'
            401:
                description: not authenticated
                schema:
                    $ref: '#/definitions/ErrorMessage'
        """
        return self.model.update_one_response(request)

    @route('permissions')
    def get_permissions(self, request):
        """
        ---
        summary: Fetch permissions the authenticated user to perform actions
        tags:
            - user
            - permission
        responses:
            200:
                description: successfully updated
                schema:
                    $ref: '#/definitions/UserPermissions'
        """
        return request.json_response(user_permissions(request))
