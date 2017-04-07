from lux.models import Schema, fields, UniqueField
from lux.ext.rest import RestRouter, route
from lux.ext.odm import Model


URI = 'groups'


class GroupSchema(Schema):
    name = fields.Slug(validate=UniqueField(), required=True)
    permissions = fields.List(
        fields.Nested('PermissionSchema'),
        description='List of permissions for this group'
    )

    class Meta:
        model = URI
        exclude = ('users',)


class GroupCRUD(RestRouter):
    model = Model(
        URI,
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
        return self.model.get_list_response(request)

    @route('<id>')
    def get_one(self, request):
        """
        ---
        summary: get a group by its id or name
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
        return self.model.get_one_response(request)
