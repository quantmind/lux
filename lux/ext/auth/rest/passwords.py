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
    """Endpoints for password recovery
    """
    model = PasswordResetModel(
        'passwords',
        model_schema=RegistrationSchema,
        create_schema=ChangePasswordRequestSchema,
        type=2
    )

    def post(self, request):
        """
        ---
        summary: Create a new password reset registration
        tags:
            - authentication
            - password
        responses:
            201:
                description: A new password-reset registration was
                    successfully created
                schema:
                    $ref: '#/definitions/Registration'
        """
        ensure_service_user(request)
        return self.model.create_response(request)

    @route('<id>/change')
    def post_change(self, request):
        """
        ---
        summary: Change a password
        description: Change password for a user
        tags:
            - authentication
            - password
        responses:
            204:
                description: Password change was successful
            400:
                description: Bad Token
                schema:
                    $ref: '#/definitions/ErrorMessage'
            401:
                description: Token missing or expired
                schema:
                    $ref: '#/definitions/ErrorMessage'
            404:
                description: Activation id not found
                schema:
                    $ref: '#/definitions/ErrorMessage'
        """
        return self.model.confirm_response(request)
