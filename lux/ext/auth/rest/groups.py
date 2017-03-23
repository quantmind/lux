from lux.extensions.rest import CRUD, RestField

from . import RestModel


class GroupCRUD(CRUD):
    model = RestModel(
        'group',
        'create-group',
        'group',
        id_field='name',
        fields=[RestField('permissions', model='permissions')]
    )
