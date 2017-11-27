"""User schemas and REST routes for the authenticated user
"""
from pulsar.api import Http401
from pulsar.utils.importer import module_attribute

from lux.ext.rest import RestRouter, route
from lux.models import fields, Schema
from lux.ext.odm import Model, Related

from .permissions import PermissionSchema
from ..permissions import user_permissions


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
    groups = fields.List(
        Related('name')
    )

    class Meta:
        model = URI
        exclude = ('password', 'superuser')


class UserUpdateSchema(UserSchema):

    class Meta:
        model = URI
        exclude = ('password', 'superuser', 'groups', 'id')


class UserQuerySchema(Schema):

    class Meta:
        model = URI
        exclude = ('password', 'groups')


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
    tags:
        - user
    """
    model = UserModel('user', UserSchema, authenticated=True)

    @route(default_response_schema=UserSchema,
           responses=(400, 401, 403))
    def get(self, request, **kw):
        """
        ---
        summary: get the authenticated user
        responses:
            200:
                description: the authenticated user

        """
        return self.model.get_one_response(request, **kw)

    @route(default_response_schema=UserSchema,
           body_schema=UserUpdateSchema,
           responses=(400, 401, 403))
    def patch(self, request, **kw):
        """
        ---
        summary: Update authenticated user and/or user profile
        responses:
            200:
                description: successfully updated
        """
        return self.model.update_one_response(request, **kw)

    @route('permissions',
           default_response_schema=PermissionSchema)
    def get_permissions(self, request, **kw):
        """
        ---
        summary: Fetch permissions the authenticated user to perform actions
        tags:
            - permission
        responses:
            200:
                description: User permissions
        """
        return request.json_response(user_permissions(request, **kw))
