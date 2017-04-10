from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from odm import declared_attr
from lux.ext import odm
from lux.utils.text import engine

from odm.types import JSONType, UUIDType


Model = odm.model_base('applications')


class Plugin(Model):
    id = Column(UUIDType(binary=False), primary_key=True,
                doc='plugin unique id')
    name = Column(String(32), doc='plugin unique name',
                  unique=True, nullable=False)

    def __str__(self):
        return self.name


class AppPlugin(Model):
    config = Column(JSONType)

    @declared_attr
    def plugin_id(cls):
        return Column(
            UUIDType,
            ForeignKey('plugin.id', ondelete='CASCADE'),
            primary_key=True
        )

    @declared_attr
    def app_id(cls):
        return Column(
            UUIDType,
            ForeignKey('appdomain.id', ondelete='CASCADE'),
            primary_key=True,
        )

    @declared_attr
    def app(cls):
        return relationship("AppDomain", backref='plugins')


class AppDomain(Model):
    id = Column(UUIDType(binary=False),
                primary_key=True,
                doc='application unique id')
    config = Column(JSONType,
                    doc='application configuration document')


class AppModelMixin:

    @classmethod
    def plural(cls):
        return engine.plural(cls.__name__.lower())

    # application that owns this worker
    @odm.declared_attr
    def application_id(cls):
        return Column(
            UUIDType,
            ForeignKey('appdomain.id', ondelete='CASCADE'),
            nullable=False
        )

    @odm.declared_attr
    def application(cls):
        return relationship("AppDomain", backref=cls.plural())
