"""API urls for password recovery
"""
from pulsar.api import MethodNotAllowed

from lux.models import Schema, fields

from .registrations import RegistrationModel
from . import ServiceCRUD, ensure_service_user


class PasswordSchema(Schema):
    password = fields.Password(maxlength=128)
    password_repeat = fields.Password(
        label='Confirm password',
        data_check_repeat='password'
    )

    def clean(self):
        password = self.cleaned_data['password']
        password_repeat = self.cleaned_data['password_repeat']
        if password != password_repeat:
            raise fields.ValidationError('Passwords did not match')


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


class PasswordsCRUD(ServiceCRUD):
    """Endpoints for password recovery
    """
    model = PasswordResetModel(
        'passwords',
        form='password-recovery',
        postform='reset-password',
        type=2
    )
