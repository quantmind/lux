from datetime import datetime
from enum import Enum

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from lux import forms
from lux.forms import Layout, Fieldset, Submit
from lux.core import LuxExtension
from lux.extensions import odm
from lux.extensions.odm import RestModel, odm_models
from lux.extensions.rest import RelationshipField, UniqueField, RestField, CRUD

from odm.types import ChoiceType

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.auth']

AUTHENTICATION_BACKENDS = ['lux.extensions.auth:TokenBackend']
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
API_URL = ''
DEFAULT_POLICY = [
    {
        "resource": '*',
        "action": "read"
    }
]


class TestEnum(Enum):
    opt1 = 1
    opt2 = 2


def odm_json(request, data):
    models = odm_models(request.app)
    for instance in data:
        model = models.get(instance.__class__.__name__.lower())
        if model:
            yield model.tojson(request, instance, in_list=True, safe=True)


class Extension(LuxExtension):

    def api_sections(self, app):
        return [CRUDTask(),
                CRUDPerson(),
                CRUDContent()]

    def on_loaded(self, app):
        app.forms['task'] = Layout(
            TaskForm,
            Fieldset(all=True),
            Submit('submit')
        )
        app.forms['person'] = Layout(
            PersonForm,
            Fieldset(all=True),
            Submit('submit')
        )

    def on_after_flush(self, app, session):
        request = session.request
        if not request:
            return
        if request.cache.new_items is None:
            request.cache.new_items = []
            request.cache.old_items = []
            request.cache.del_items = []
        request.cache.new_items.extend(odm_json(request, session.new))
        request.cache.old_items.extend(odm_json(request, session.dirty))
        request.cache.del_items.extend(odm_json(request, session.deleted))

    def on_before_commit(self, app, session):
        request = session.request
        if not request:
            return
        if request.cache.new_items_before_commit is None:
            request.cache.new_items_before_commit = []
        request.cache.new_items_before_commit.extend(
            odm_json(request, session.new)
        )


Model = odm.model_base('odmtest')


# ODM Models
class Person(Model):
    id = Column(Integer, primary_key=True)
    username = Column(String(250), unique=True)
    name = Column(String(250))


class Task(Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(250))
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)
    enum_field = Column(ChoiceType(TestEnum, impl=Integer),
                        default=TestEnum.opt1)
    desc = Column(String(250))

    @odm.declared_attr
    def assigned_id(cls):
        return Column(Integer, ForeignKey('person.id'))

    @odm.declared_attr
    def assigned(cls):
        return relationship('Person', backref='tasks')


class Content(Model):
    id = Column(Integer, primary_key=True)
    group = Column(String(30), nullable=False)
    name = Column(String(60), nullable=False)

    @property
    def path(self):
        return '%s/%s' % (self.group, self.name)


class TaskForm(forms.Form):
    model = 'tasks'
    subject = forms.CharField()
    done = forms.BooleanField(default=False)
    assigned = RelationshipField('people', required=False)
    enum_field = forms.ChoiceField(options=TestEnum, default='opt1')
    desc = forms.CharField(required=False)


class PersonForm(forms.Form):
    model = 'people'
    username = forms.CharField(validator=UniqueField())
    name = forms.CharField(required=True)


class CRUDTask(CRUD):
    model = RestModel('task', 'task', 'task',
                      fields=[RestField('assigned',
                                        model='people',
                                        field='assigned_id')])


class CRUDPerson(CRUD):
    model = RestModel('person', 'person', 'person', url='people')


class CRUDContent(CRUD):
    model = RestModel('content', id_field='path')
