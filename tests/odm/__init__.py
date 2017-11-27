from datetime import datetime
from enum import Enum

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey

from lux.core import LuxExtension
from lux.models import Schema, fields, UniqueField
from lux.ext import odm
from lux.ext.odm import Model
from lux.ext.rest import RestRouter

from odm.types import ChoiceType

from tests.config import *  # noqa

EXTENSIONS = ['lux.ext.base',
              'lux.ext.odm',
              'lux.ext.rest',
              'lux.ext.auth']

AUTHENTICATION_BACKENDS = ['lux.ext.auth:TokenBackend']
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
    models = request.app.models
    for instance in data:
        model = models.get(instance.__class__.__name__.lower())
        if model:
            yield model.tojson(request, instance, in_list=True, safe=True)


class Extension(LuxExtension):

    def api_sections(self, app):
        return [CRUDTask(),
                CRUDPerson(),
                CRUDContent()]

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


dbModel = odm.model_base('odmtest')


# ODM Models
class Person(dbModel):
    id = Column(Integer, primary_key=True)
    username = Column(String(250), unique=True)
    name = Column(String(250))


class Task(dbModel):
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


class Content(dbModel):
    id = Column(Integer, primary_key=True)
    group = Column(String(30), nullable=False)
    name = Column(String(60), nullable=False)

    @property
    def path(self):
        return '%s/%s' % (self.group, self.name)


class TaskSchema(Schema):
    assigned = fields.Nested('PersonSchema')

    class Meta:
        model = 'tasks'


class PersonSchema(Schema):
    username = fields.String(validator=UniqueField)
    name = fields.String(required=True)


class CRUDTask(RestRouter):
    model = Model(
        'tasks',
        model_schema=TaskSchema
    )


class CRUDPerson(RestRouter):
    model = Model(
        'people',
        model_schema=PersonSchema,
        db_name='person'
    )


class CRUDContent(RestRouter):
    model = Model('content', id_field='path')
