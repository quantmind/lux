"""API urls for password recovery and reset
"""
from pulsar import MethodNotAllowed, Http404

from lux.core import http_assert

from . import ServiceCRUD, ensure_service_user
from .registrations import RegistrationModel


class PasswordResetModel(RegistrationModel):

    def get_instance(self, request, **kw):
        ensure_service_user(request, MethodNotAllowed)
        return super().get_instance(request, **kw)

    def update_model(self, request, instance, data, session=None, **kw):
        if not instance.id:
            return super().update_model(request, instance, data,
                                        session=session, **kw)
        reg = self.instance(instance).obj
        http_assert(reg.type == 2, Http404)
        #
        backend = request.cache.auth_backend
        password = data['password']
        with self.session(request, session=session) as session:
            user = reg.user
            user.password = backend.password(request, password)
            session.add(user)
            session.delete(reg)


class PasswordsCRUD(ServiceCRUD):
    """Endpoints for password recovery
    """
    model = PasswordResetModel.create(
        form='password-recovery',
        postform='reset-password',
        url='passwords',
        type=2
    )
