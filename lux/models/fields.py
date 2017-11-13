import uuid
import enum
from functools import partial
from datetime import datetime

from marshmallow.fields import (
    Field, Raw, Dict, List, String, Number, Integer, Decimal,
    Boolean, FormattedString, Float, LocalDateTime,
    Time, Date, TimeDelta, Url, URL, Email, Method, Function, Str, Bool,
    Int, Constant,
    UUID as MaUUID,
    Nested as MaNested,
    DateTime as MaDateTime
)
from marshmallow import class_registry
from lux.openapi.ext.marshmallow import map_to_openapi_type

from pulsar.utils.slugify import slugify

from .model import app_schemas, app_cache
from .schema import Schema


__all__ = [
    'Field',
    'Raw',
    'Nested',
    'Dict',
    'List',
    'String',
    'UUID',
    'Number',
    'Integer',
    'Decimal',
    'Boolean',
    'FormattedString',
    'Float',
    'DateTime',
    'LocalDateTime',
    'Time',
    'Date',
    'TimeDelta',
    'Url',
    'URL',
    'Email',
    'Method',
    'Function',
    'Str',
    'Bool',
    'Int',
    'Constant',
    #
    'Password',
    'Slug',
    'Enum'
]


class Nested(MaNested):

    @property
    def schema(self):
        """The nested Schema object
        """
        if isinstance(self.nested, str):
            schema_class = class_registry.get_class(self.nested, True)
            if schema_class:
                if isinstance(schema_class, list):
                    schema_class = schema_class[-1]
                return schema_class(many=self.many)
        return super().schema


@map_to_openapi_type(String)
class Password(String):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.metadata['html_type'] = 'hidden'
        self.validators.append(password_validate)


@map_to_openapi_type(String)
class Slug(String):
    validation_error = ('Only lower case, alphanumeric characters and '
                        'hyphens are allowed')

    def __init__(self, *args, separator='-', **kw):
        kw.setdefault('autocorrect', 'off')
        kw.setdefault('autocapitalize', 'none')
        super().__init__(*args, **kw)
        self.validators.append(partial(slug_validator, separator))


@map_to_openapi_type(MaDateTime)
class DateTime(MaDateTime):

    def _deserialize(self, value, attr, data):
        if isinstance(value, datetime):
            return value
        return super()._deserialize(value, attr, data)


@map_to_openapi_type(MaUUID)
class UUID(MaUUID):

    def _validated(self, value):
        return super()._validated(value).hex


class Enum(Field):

    def _serialize(self, value, attr, obj):
        return value.name if isinstance(value, enum.Enum) else value


def password_validate(value):
    if value != value.strip():
        return False


def slug_validator(separator, value):
    return slugify(value, separator=separator) == value


@app_cache
def app_nested_schemas(app):
    return {}


Schema.TYPE_MAPPING[datetime] = DateTime
Schema.TYPE_MAPPING[uuid.UUID] = UUID
