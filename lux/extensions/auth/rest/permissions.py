from lux.extensions.rest import CRUD

from . import RestModel


class PermissionCRUD(CRUD):
    model = RestModel(
        'permission',
        form='permission',
        updateform='permission',
        id_field='name',
        hidden=('id', 'policy')
    )
