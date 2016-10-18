from lux.extensions.rest import CRUD

from .registrations import RegistrationModel


class PasswordsCRUD(CRUD):
    """Endpoints for password recovery
    """
    model = RegistrationModel.create(
        form='password-recovery',
        url='passwords',
        type=2
    )
