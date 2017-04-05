from lux.models import Schema, fields, UniqueField, registry, html
from lux.ext.rest import RestRouter
from lux.ext.odm import Model


class GroupSchema(Schema):
    model = 'groups'
    name = fields.Slug(validate=UniqueField(), required=True)
    permissions = fields.List(
        fields.Nested('PermissionSchema'),
        description='List of permissions for this group'
    )


class GroupCRUD(RestRouter):
    model = Model(
        'groups',
        model_schema=GroupSchema,
        id_field='name'
    )

    def get(self, request):
        """
        ---
        summary: get a list of groups
        tags:
            - user
            - group
        responses:
            200:
                description: a list of groups
                schema:
                    $ref: '#/definitions/User'
            401:
                description: not authenticated
                schema:
                    $ref: '#/definitions/ErrorMessage'
        """
        return self.model.get_list(request)


registry['create-group'] = html.Layout(
    GroupSchema,
    html.Fieldset(all=True),
    html.Submit('Create new group')
)


registry['group'] = html.Layout(
    GroupSchema,
    html.Fieldset(all=True),
    html.Submit('Update group')
)
