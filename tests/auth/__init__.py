from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from lux import forms
from lux.core import LuxExtension
from lux.extensions.rest import CRUD
from lux.extensions import odm

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.rest',
              'lux.extensions.odm',
              'lux.extensions.auth']

API_URL = ''
DEFAULT_PERMISSION_LEVEL = 'none'
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
COMING_SOON_URL = 'coming-soon'
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
DEFAULT_POLICY = [
    {
        "resource": "objectives:*",
        "action": "*"
    },
    {
        "resource": "objectives:*:deadline",
        "action": "*",
        "effect": "deny",
        "condition": "user.is_anonymous()"
    }
]

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


class ObjectiveCRUD(CRUD):
    model = odm.RestModel('objective', ObjectiveForm, ObjectiveForm)


class SecretCRUD(CRUD):
    model = odm.RestModel('secret', SecretForm, SecretForm)
