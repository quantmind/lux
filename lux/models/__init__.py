"""Lux models are built on top of

* Marshmallow Schemas
* SqlAlchemy models
"""
from marshmallow import ValidationError, post_dump, post_load
from marshmallow.validate import OneOf

import inflect

from .schema import Schema, resource_name, get_schema_class
from .component import Component
from .model import ModelContainer, Model
from .query import Query, Session
from .unique import UniqueField

inflect = inflect.engine()


__all__ = [
    'Schema',
    'Component',
    'ValidationError',
    'resource_name',
    'get_schema_class',
    #
    'post_dump',
    'post_load',
    'OneOf',
    #
    'inflect',
    #
    'ModelContainer',
    'Model',
    'Session',
    'Query',
    'UniqueField'
]
