"""REST endpoints handlers
"""
from lux.core import route
from lux.utils.crypt import create_uuid, create_token
from lux.extensions.rest import CRUD
from lux.extensions.odm import RestModel
from lux.utils.token import encode_json

from .forms import ApplicationForm


class ApplicationModel(RestModel):

    def create_instance(self):
        model = self.db_model()
        return model(id=create_uuid(), token=create_token())

    def jwt(self, request, instance):
        data = self.tojson(request, instance)
        secret = data.pop('token')
        return encode_json(data, secret,
                           algorithm=request.config['JWT_ALGORITHM'])


class ApplicationCRUD(CRUD):
    model = ApplicationModel(
        'application',
        form=ApplicationForm,
        updateform=ApplicationForm
    )

    @route('<id>/token', method=('post',))
    def token(self, request):
        """Regenerate the root token for this application
        """
        pass
