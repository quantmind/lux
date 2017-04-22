from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from lux.core import LuxExtension
from lux.models import Schema, fields
from lux.ext.rest import RestRouter
from lux.ext.odm import Model, model_base

from tests.config import *  # noqa

EXTENSIONS = ['lux.ext.base',
              'lux.ext.rest',
              'lux.ext.odm',
              'lux.ext.auth']

API_URL = ''
DEFAULT_CONTENT_TYPE = 'application/json'
COMING_SOON_URL = 'coming-soon'
DATASTORE = 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'
DEFAULT_POLICY = [
    {
        "resource": [
            "passwords:*",
            "mailinglist:*"
        ],
        "action": "*"
    },
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

dbModel = model_base('odmtest')


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


class ObjectiveSchema(Schema):
    subject = fields.String()
    deadline = fields.String()
    outcome = fields.String()
    done = fields.Boolean(default=False)


class SecretSchema(Schema):
    value = fields.String(required=False)


class ObjectiveCRUD(RestRouter):
    model = Model(
        'objective',
        model_schema=ObjectiveSchema
    )


class SecretCRUD(RestRouter):
    model = Model(
        'secrets',
        model_schema=SecretSchema
    )
