from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

import lux

from lux import forms
from lux.extensions import odm
from lux.extensions.auth.views import UserCRUD, GroupCRUD, PermissionCRUD

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.admin',
              'lux.extensions.auth']

API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend',
                           'lux.extensions.auth.BrowserBackend']

Model = odm.model_base('odmtest')


class Extension(lux.Extension):

    def api_sections(self, app):
        return [UserCRUD(), GroupCRUD(), PermissionCRUD(), ObjectiveCRUD()]


class Objective(Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(250))
    deadline = Column(String(250))
    outcome = Column(String(250))
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)


class ObjectiveForm(forms.Form):
    subject = forms.CharField(required=False)
    deadline = forms.CharField(required=False)
    outcome = forms.CharField(required=False)
    done = forms.BooleanField(default=False)


class ObjectiveCRUD(odm.CRUD):
    model = odm.RestModel('objective', ObjectiveForm)
