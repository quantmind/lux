"""Lux models are built on top of

* Marshmallow Schemas
* SqlAlchemy models
"""
from marshmallow import fields, ValidationError
from marshmallow.validate import OneOf

import inflect

from .schema import Schema, schema_registry
from .component import Component
from .model import ModelContainer, Model
from .query import Query
from .extra import Slug, Password
from .unique import UniqueField
from .registry import registry, get_form, get_form_class, get_form_layout
from . import html


inflect = inflect.engine()


__all__ = [
    'Schema',
    'Component',
    'fields',
    'html',
    'ValidationError',
    'schema_registry',
    #
    'OneOf',
    #
    'inflect',
    #
    'registry',
    'get_form',
    'get_form_class',
    'get_form_layout',
    #
    'ModelContainer',
    'Model',
    'Query',
    'UniqueField'
]


fields.Password = Password
fields.Slug = Slug
