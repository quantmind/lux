from lux.ext.rest import CRUD, RestField
from lux.ext.odm import RestModel


class GroupCRUD(CRUD):
    model = RestModel(
        'group',
        'create-group',
        'group',
        id_field='name',
        fields=[RestField('permissions', model='permissions')]
    )
