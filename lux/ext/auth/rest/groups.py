from lux.models import Schema, fields, UniqueField
from lux.ext.rest import RestRouter, route
from lux.ext.odm import Model


URI = 'groups'


class GroupSchema(Schema):
    name = fields.Slug(validate=UniqueField(URI), required=True)
    permissions = fields.List(
        fields.Nested('PermissionSchema'),
        description='List of permissions for this group'
    )

    class Meta:
        model = URI
        exclude = ('users',)


class GroupPathSchema(Schema):
    id = fields.String(required=True,
                       description='group unique ID or name')


class GroupModel(Model):

    def __call__(self, data, session):
        data.pop('permissions', None)
        group = super().__call__(data, session)
        return group


class GroupCRUD(RestRouter):
    model = GroupModel(
        URI,
        model_schema=GroupSchema,
        create_schema=GroupSchema
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
                type: array
                items:
                    $ref: '#/definitions/Group'
            401:
                description: not authenticated
                schema:
                    $ref: '#/definitions/ErrorMessage'
        """
        return self.model.get_list_response(request)

    def post(self, request):
        """
        ---
        summary: Create a new group
        tags:
            - group
        responses:
            201:
                description: A new Group has was created
                schema:
                    $ref: '#/definitions/Group'
        """
        return self.model.create_response(request)

    @route('<id>', path_schema=GroupPathSchema)
    def get_one(self, request):
        """
        ---
        summary: get a group by its id or name
        tags:
            - user
            - group
        responses:
            200:
                description: the group matching the id or name
                schema:
                    $ref: '#/definitions/Group'
            401:
                description: not authenticated
                schema:
                    $ref: '#/definitions/ErrorMessage'
        """
        return self.model.get_one_response(request)
