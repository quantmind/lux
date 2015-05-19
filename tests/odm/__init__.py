from datetime import datetime

import lux
from lux import forms
from lux.extensions import odm

from sqlalchemy import Column, Integer, String, Boolean, DateTime


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']


class Extension(lux.Extension):

    def api_sections(self, app):
        return [CRUDTask('/tasks')]


class TaskForm(forms.Form):
    subject = forms.CharField(required=True)
    done = forms.BooleanField(default=False)


class CRUDTask(odm.CRUD):
    model = odm.RestModel('task', TaskForm)
    addform = TaskForm


class Task(odm.Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(250))
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)
