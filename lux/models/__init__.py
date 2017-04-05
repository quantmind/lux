"""Lux models are built on top of

* Marshmallow Schemas
* SqlAlchemy models
"""
from marshmallow import Schema, fields, ValidationError
from marshmallow.validate import OneOf

from .component import Component
from .model import ModelContainer, Model
from .query import Query
from .extra import Slug, Password
from .unique import UniqueField
from .registry import registry, get_form, get_form_class, get_form_layout
from . import html


__all__ = [
    'Schema',
    'Component',
    'fields',
    'html',
    'ValidationError',
    #
    'OneOf',
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

