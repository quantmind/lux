"""REST endpoints handlers
"""
from lux.core import route
from lux.utils.crypt import create_uuid, generate_secret
from lux.extensions.rest import CRUD
from lux.extensions.odm import RestModel
from lux.utils.token import encode_json

from .forms import ApplicationForm


class ApplicationModel(RestModel):

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


class ApplicationCRUD(CRUD):
    model = ApplicationModel(
        'appdomain',
        url='applications',
        form=ApplicationForm,
        updateform=ApplicationForm
    )

    @route('<id>/token', method=('post',))
    def token(self, request):
        """Regenerate the root token for this application
        """
        pass
