from datetime import datetime

import lux
from lux import forms
from lux.extensions import odm

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']


class Extension(lux.Extension):

    def api_sections(self, app):
        return [CRUDTask(), CRUDPerson()]


class TaskForm(forms.Form):
    subject = forms.CharField(required=True)
    done = forms.BooleanField(default=False)
    assigned = odm.RelationshipField(model='person', required=False)


class PersonForm(forms.Form):
    model = 'person'
    username = forms.CharField(validator=odm.UniqueField())
    name = forms.CharField(required=True)


class CRUDTask(odm.CRUD):
    model = odm.RestModel('task', TaskForm)


class CRUDPerson(odm.CRUD):
    model = odm.RestModel('person', PersonForm, url='people')


class Person(odm.Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(250), unique=True)
    name = Column(String(250))


class Task(odm.Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(250))
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)
    assigned = Column(Integer, ForeignKey('person.id'))
