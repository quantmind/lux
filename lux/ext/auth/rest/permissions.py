import json

from lux.ext.rest import RestRouter, PolicySchema, route
from lux.ext.odm import Model
from lux.models import Schema, fields


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
    model = Model(
        'permissions',
        model_schema=PermissionSchema,
        create_schema=PermissionSchema,
        update_schema=PermissionSchema
    )

    def get(self, request):
        """
        ---
        summary: List permissions documents
        tags:
            - permission
        responses:
            200:
                description: List of permissions matching filters
                type: array
                items:
                    $ref: '#/definitions/Permission'
        """
        return self.model.list_response(request)

    def post(self, request):
        """
        ---
        summary: Create a new permission document
        tags:
            - permission
        responses:
            201:
                description: A new permission document was successfully created
                schema:
                    $ref: '#/definitions/Permission'
        """
        return self.model.create_response(request)

    @route('<id>', responses=(400, 401, 404))
    def patch(self, request):
        """
        ---
        summary: Updated an existing permission document
        tags:
            - permission
        responses:
            200:
                description: Permission document was successfully updated
                schema:
                    $ref: '#/definitions/Permission'
        """
        return self.model.update_response(request)

    @route('<id>', responses=(204, 400, 401, 404))
    def delete(self, request):
        """
        ---
        summary: Delete an existing permission document
        tags:
            - permission
        """
