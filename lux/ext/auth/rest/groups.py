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
    """
    ---
    summary: Group path
    description: provide operations for groups
    tags:
        - group
    """
    model = GroupModel(URI, GroupSchema)

    @route(default_response_schema=[GroupSchema],
           responses=(401, 403))
    def get(self, request):
        """
        ---
        summary: get a list of groups
        responses:
            200:
                description: a list of groups
        """
        return self.model.get_list_response(request)

    @route(default_response=201,
           default_response_schema=GroupSchema,
           body_schema=GroupSchema,
           responses=(401, 403))
    def post(self, request, **kw):
        """
        ---
        summary: Create a new group
        """
        return self.model.create_response(request, **kw)

    @route(GroupPathSchema,
           default_response_schema=GroupSchema,
           responses=(401, 403, 404))
    def get_one(self, request, **kw):
        """
        ---
        summary: get a group by its id or name
        responses:
            200:
                description: the group matching the id or name
        """
        return self.model.get_one_response(request, **kw)

    @route(GroupPathSchema,
           default_response_schema=GroupSchema,
           body_schema=GroupSchema,
           responses=(401, 403, 404, 422))
    def patch_one(self, request, **kw):
        """
        ---
        summary: get a group by its id or name
        responses:
            200:
                description: the group matching the id or name
        """
        return self.model.update_one_response(request, **kw)
