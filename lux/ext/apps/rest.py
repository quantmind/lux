"""REST endpoints handlers
"""
from lux.core import route
from lux.utils.crypt import create_uuid, generate_secret
from lux.ext.rest import RestRouter
from lux.ext.odm import Model
from lux.utils.token import encode_json

from .schema import ApplicationSchema, PluginSchema


class ApplicationModel(Model):

    def create_instance(self):
        model = self.db_model()
        token = generate_secret(64)
        return model(id=create_uuid(), secret=token)

    def regenerate_token(self, request, instance, session=None):
        app_domain = self.instance(instance).obj
        with self.session(request, session=session) as session:
            app_domain.secret = generate_secret(64)
            session.add(app_domain)
        return app_domain.secret

    def jwt(self, request, instance):
        data = self.tojson(request, instance)
        secret = data.pop('secret')
        return encode_json(data, secret,
                           algorithm=request.config['JWT_ALGORITHM'])


class ApplicationCRUD(RestRouter):
    model = ApplicationModel(
        'applications',
        model_schema=ApplicationSchema,
        db_name='appdomain'
    )

    def get(self, request):
        """
        ---
        summary: Applications available
        description: List all plugins available in the server. This endpoint
            is only available for the master user
        tags:
            - application
            - plugin
        responses:
            200:
                description: a paginated list of application objects
                type: array
                items:
                    $ref: '#/definitions/Application'
        """
        return self.model.get_list_response(request)

    def post(self, request):
        """
        ---
        summary: Create a new application
        description: Create a new application ready for use
        tags:
            - application
            - plugin
        responses:
            201:
                description: return the newly created application
                schema:
                    $ref: '#/definitions/Application'
        """
        return self.model.create_response(request)

    @route('<id>', responses=(400, 401, 404))
    def get_app(self, request):
        """
        ---
        summary: Get an existing application
        description: Return the application matching the id or name
        tags:
            - application
            - plugin
        responses:
            200:
                description: return the application
                schema:
                    $ref: '#/definitions/Application'
        """
        return self.model.get_response(request)

    @route('<id>/token', method=('post',))
    def token(self, request):
        """Regenerate the root token for this application
        """
        pass


class PluginCRUD(RestRouter):
    model = Model(
        'plugins',
        model_schema=PluginSchema
    )

    def get(self, request):
        """
        ---
        summary: Plugins available
        description: List all plugins available in the server
        tags:
            - application
            - plugin
        responses:
            200:
                description: a paginated list of plugin objects
                type: array
                items:
                    $ref: '#/definitions/Plugin'
        """
        return self.model.get_list_response(request)
