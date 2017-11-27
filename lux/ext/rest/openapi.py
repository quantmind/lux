from lux.models import Schema, fields

from .rest import RestRouter
from .route import route


default_plugins = ['lux.openapi.ext.lux']


class APISchema(Schema):
    BASE_PATH = fields.String(required=True)
    TITLE = fields.String(required=True)
    DESCRIPTION = fields.String()
    VERSION = fields.String(default='0.1.0')
    SPEC_PLUGINS = fields.List(fields.String(), default=default_plugins)
    SPEC_PATH = fields.String(default='spec',
                              description='path of api specification document')
    MODEL = fields.String(default='*')
    CORS = fields.Boolean(default=True)


api_schema = APISchema()


class Specification(RestRouter):
    api = None

    @route()
    def get(self, request):
        """
        ---
        summary: OpenAPI specification document
        responses:
            200:
                description: The OpenAPI specification document
        """
        if not self.api:
            pass
        spec = self.api.spec_dict()
        spec['servers'] = [
            dict(
                url='%s://%s' % (request.scheme, request.get_host()),
                description="default server"
            )
        ]
        return request.json_response(spec)
