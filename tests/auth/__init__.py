from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from lux import forms
from lux.core import LuxExtension, route
from lux.extensions import odm, rest
from lux.utils.auth import ensure_authenticated
from lux.extensions.auth.forms import UserModel, UserForm
from lux.extensions.auth.views import (UserCRUD, GroupCRUD, PermissionCRUD,
                                       RegistrationCRUD)

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.admin',
              'lux.extensions.auth']

API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
DEFAULT_PERMISSION_LEVELS = {
    'group': 'none',
    'registration': 'none',
    'secret': 'none',
    'objective': '*',
    'objective:subject': 'none',
    'objective:deadline': ('read', 'update'),
    'objective:outcome': 'read'
}


Model = odm.model_base('odmtest')


class Extension(LuxExtension):

    def api_sections(self, app):
        return [UserRest(),
                UserCRUD(),
                GroupCRUD(),
                PermissionCRUD(),
                RegistrationCRUD(),
                ObjectiveCRUD(),
                SecretCRUD()]


class Objective(Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(250))
    deadline = Column(String(250))
    outcome = Column(String(250))
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)


class Secret(Model):
    id = Column(Integer, primary_key=True)
    value = Column(String(250))
    created = Column(DateTime, default=datetime.utcnow)


class ObjectiveForm(forms.Form):
    subject = forms.CharField(required=False)
    deadline = forms.CharField(required=False)
    outcome = forms.CharField(required=False)
    done = forms.BooleanField(default=False)


class SecretForm(forms.Form):
    value = forms.CharField(required=False)


class ObjectiveCRUD(odm.CRUD):
    model = odm.RestModel('objective', ObjectiveForm, ObjectiveForm)


class SecretCRUD(odm.CRUD):
    model = odm.RestModel('secret', SecretForm, SecretForm)


def user_model():
    return UserModel('user',
                     None,
                     UserForm,
                     id_field='username',
                     repr_field='username',
                     url='user',
                     exclude=('password',))


class UserRest(odm.RestRouter):
    """Rest view for the authenticated user
    No CREATE, simple read, updates and other update-type operations
    """
    model = user_model()

    def get_instance(self, request, session=None):
        user = ensure_authenticated(request)
        return super().get_instance(request, session=session, id=user.id)

    def get(self, request):
        """
        Get the authenticated user
        """
        user = self.get_instance(request)
        model = self.model(request)
        data = model.serialise(request, user)
        return self.json(request, data)

    def post(self, request):
        """
        Update authenticated user and/or user profile
        """
        user = self.get_instance(request)
        model = self.model(request.app)
        form = model.form(request, data=request.body_data())
        if form.is_valid():
            user = model.update_model(request, user, form.cleaned_data)
            data = model.serialise(request, user)
        else:
            data = form.tojson()
        return self.json(request, data)

    @route('permissions', method=['get', 'options'])
    def get_permissions(self, request):
        """Check permissions the authenticated user has for a
        given action.
        """
        if request.method == 'options':
            request.app.fire('on_preflight', request, methods=['GET'])
            return request.response

        resources = request.url_data.get('resource', ())
        if not isinstance(resources, (list, tuple)):
            resources = (resources,)
        backend = request.cache.auth_backend
        perms = {}
        for resource in resources:
            vals = {}
            perms[resource] = vals
            for name in rest.PERMISSION_LEVELS:
                vals[name] = backend.has_permission(request, resource, name)
        return self.json(request, perms)
