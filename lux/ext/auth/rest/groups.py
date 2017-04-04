from lux.ext.rest import RestModel
from lux.ext.odm import Model


class GroupCRUD(RestModel):
    model = Model(
        'groups',
        'create-group',
        'group',
        id_field='name'
    )
