from lux.ext.rest import CRUD
from lux.ext.odm import Model


class GroupCRUD(CRUD):
    model = Model(
        'group',
        'create-group',
        'group',
        id_field='name'
    )
