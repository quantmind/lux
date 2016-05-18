from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from lux import forms
from lux.core import LuxExtension
from lux.extensions import odm

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.odm',
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
        return [ObjectiveCRUD(),
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
