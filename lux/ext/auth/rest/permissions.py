import json

from lux.ext.rest import CRUD, PolicySchema
from lux.models import Schema, ModelSchema, fields, html

from . import RestModel


class PermissionSchema(ModelSchema):
    model = 'permissions'
    name = fields.String(required=True)
    description = fields.String(rows=2, html_type='textarea')
    policy = fields.List(
        PolicySchema(),
        ace=json.dumps({'mode': 'json'})
    )


class PermissionCRUD(CRUD):
    model = RestModel(
        'permissions',
        model_schema=PermissionSchema(),
        create_schema='create-permission',
        update_schema='permission',
        id_field='name',
        hidden=('id', 'policy')
    )


html.reg['create-permission'] = html.Layout(
    PermissionSchema,
    html.Fieldset(all=True),
    html.Submit('Create new permissions')
)


html.reg['permission'] = html.Layout(
    PermissionSchema(),
    html.Fieldset(all=True),
    html.Submit('Update permissions')
)
