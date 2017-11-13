import json

from lux.ext.rest import RestRouter, route
from lux.ext.odm import Model
from lux.models import Schema, fields

from ..permissions import PolicySchema


class PermissionSchema(Schema):
    model = 'permissions'
    name = fields.String(maxLength=60, required=True)
    description = fields.String(rows=2, html_type='textarea')
    policy = fields.List(
        fields.Nested(PolicySchema),
        ace=json.dumps({'mode': 'json'})
    )

    class Meta:
        model = 'permissions'


class PermissionCRUD(RestRouter):
    """
    ---
    summary: Permissions
    tags:
        - permission
    """
    model = Model('permissions', PermissionSchema)

    @route(default_response_schema=[PermissionSchema])
    def get(self, request, **kw):
        """
        ---
        summary: List permissions documents
        responses:
            200:
                description: List of permissions matching filters
        """
        return self.model.list_response(request, **kw)

    @route(default_response=201,
           body_schema=PermissionSchema,
           default_response_schema=[PermissionSchema],
           responses=(400, 401, 403, 422))
    def post(self, request, **kw):
        """
        ---
        summary: Create a new permission document
        """
        return self.model.create_response(request, **kw)

    @route('<id>', responses=(400, 401, 403, 404))
    def patch_one(self, request, **kw):
        """
        ---
        summary: Updated an existing permission document
        responses:
            200:
                description: Permission document was successfully updated
        """
        return self.model.update_response(request, **kw)

    @route('<id>',
           default_response=204,
           responses=(400, 401, 403, 404))
    def delete(self, request, **kw):
        """
        ---
        summary: Delete an existing permission document
        """
        return self.model.delete_one_response(request, **kw)
