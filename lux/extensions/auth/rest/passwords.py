"""API urls for password recovery
"""
from pulsar import MethodNotAllowed

from . import ServiceCRUD, ensure_service_user
from .registrations import RegistrationModel


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
    model = PasswordResetModel.create(
        form='password-recovery',
        postform='reset-password',
        url='passwords',
        type=2
    )
