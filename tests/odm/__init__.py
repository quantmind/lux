from datetime import datetime

import lux
from lux import forms
from lux.extensions import odm

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey


EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']


AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend']
CORS_ALLOWED_METHODS = 'GET, POST, DELETE'


class Extension(lux.Extension):

    def api_sections(self, app):
        return [CRUDTask(), CRUDPerson(), UserCRUD()]


class TaskForm(forms.Form):
    subject = forms.CharField(required=True)
    done = forms.BooleanField(default=False)
    assigned_id = odm.RelationshipField(model='person',
                                        label='assigned',
                                        required=False)


class PersonForm(forms.Form):
    model = 'person'
    username = forms.CharField(validator=odm.UniqueField())
    name = forms.CharField(required=True)


class UserForm(forms.Form):
    username = forms.CharField()
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    superuser = forms.BooleanField()
    active = forms.BooleanField()


class CRUDTask(odm.CRUD):
    model = odm.RestModel('task', TaskForm)


class CRUDPerson(odm.CRUD):
    model = odm.RestModel('person', PersonForm, url='people')


class UserCRUD(odm.CRUD):
    '''Test custom CRUD view and RestModel
    '''
    model = odm.RestModel('user',
                          UserForm,
                          columns=('username', 'active', 'superuser'),
                          exclude=('password', 'permissions'))

    def serialise_model(self, request, data, in_list=False):
        return self.model.tojson(request, data, exclude=('superuser',))


Model = odm.model_base('odmtest')


# Models
class Person(Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(250), unique=True)
    name = Column(String(250))
    tasks = relationship('Task', backref='assigned')


class Task(Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(250))
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)
    assigned_id = Column(Integer, ForeignKey('person.id'))
