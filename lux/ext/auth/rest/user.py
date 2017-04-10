from pulsar.api import Http401
from pulsar.utils.importer import module_attribute

from lux.core import route
from lux.ext.rest import RestRouter, user_permissions
from lux.models import fields, Schema
from lux.ext.odm import Model


URI = 'users'


def validate_username(session, username):
    module_attribute(session.config['CHECK_USERNAME'])(session, username)


class FullUserSchema(Schema):

    class Meta:
        model = URI


class UserSchema(Schema):
    username = fields.Slug(required=True, readOnly=True)
    joined = fields.DateTime(readOnly=True)
    email = fields.Email()
    full_name = fields.String(
        field=('first_name', 'last_name', 'username', 'email'),
        readOnly=True
    )
    groups = fields.Nested('GroupSchema', multi=True)

    class Meta:
        exclude = ('password', 'superuser')
        model = URI


class UserQuerySchema(Schema):

    class Meta:
        exclude = ('password', 'groups')
        model = URI


class UserModel(Model):

    @property
    def authenticated(self):
        return self.metadata.get('authenticated', False)

    def get_one(self, session, *args, **kwargs):
        """When authenticated is True return the current user or
        raise Http401
        """
        if self.authenticated and not (args or kwargs):
            user = session.request.cache.get('user')
            if not user.is_authenticated():
                raise Http401('token')
            return user
        return super().get_one(session, *args, **kwargs)

    def create_one(self, session, data, schema=None):
        validate_username(session, data.get('username'))
        data['password'] = session.auth.password(data.get('password'))
        return super().create_one(session, data, schema)


class UserRest(RestRouter):
    """
    ---
    summary: Rest operations for the authenticated user
    """
    model = UserModel(
        'user',
        model_schema=UserSchema,
        update_schema=UserSchema,
        query_schema=UserQuerySchema,
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
