"""API urls for password recovery
"""
from pulsar.api import MethodNotAllowed

from lux.core import AuthenticationError
from lux.models import Schema, fields, ValidationError
from lux.ext.rest import RestRouter, route

from .registrations import (
    RegistrationModel, PasswordSchema, RegistrationSchema
)
from . import ensure_service_user
from ..models import RegistrationType


class ChangePasswordRequestSchema(Schema):
    email = fields.Email(required=True)

    def post_load(self, data):
        user = self.get_user(data.request, data['email'])
        return self.create_model(data.session, user, RegistrationType.password)

    def get_user(self, request, email):
        raise ValidationError("Can't find user, sorry")


class ChangePasswordSchema(PasswordSchema):
    old_password = fields.Password(required=True)

    def clean_old_password(self, value):
        request = self.request
        user = request.cache.user
        auth_backend = request.cache.auth_backend
        try:
            if user.is_authenticated():
                auth_backend.authenticate(request, user=user, password=value)
            else:
                raise AuthenticationError('not authenticated')
        except AuthenticationError as exc:
            raise fields.ValidationError(str(exc))
        return value


class PasswordResetModel(RegistrationModel):

    def get_instance(self, request, **kw):
        ensure_service_user(request, MethodNotAllowed)
        return super().get_instance(request, **kw)

    def update_registration(self, request, reg, data, session=None):
        backend = request.cache.auth_backend
        password = data['password']
        with self.session(request, session=session) as session:
            user = reg.user
            user.password = backend.password(request, password)
            session.add(user)
            session.delete(reg)
        return {'success': True}


class PasswordsCRUD(RestRouter):
    """
    ---
    summary: Endpoints for password recovery
    tags:
        - authentication
        - password
    """
    model = PasswordResetModel('passwords', RegistrationSchema, type=2)

    @route(default_response=201,
           default_response_schema=RegistrationSchema,
           body_schema=ChangePasswordRequestSchema)
    def post(self, request):
        """
        ---
        summary: Request a new password-reset
        responses:
            201:
                description: A new password-reset request was
                    successfully created
        """
        ensure_service_user(request)
        return self.model.create_response(request)

    @route('<id>/change',
           default_response=204,
           body_schema=ChangePasswordSchema,
           responses=(400, 401, 403, 404, 422))
    def post_change(self, request):
        """
        ---
        summary: Change a password for a user
        description: given a password-reset change id,
            change the user password
        responses:
            204:
                description: Password change was successful
        """
        return self.model.confirm_response(request)
