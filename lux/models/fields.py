import uuid
from functools import partial
from datetime import datetime

from marshmallow.fields import (
    Field, Raw, Dict, List, String, Number, Integer, Decimal,
    Boolean, FormattedString, Float, DateTime, LocalDateTime,
    Time, Date, TimeDelta, Url, URL, Email, Method, Function, Str, Bool,
    Int, Constant,
    UUID as MaUUID,
    Nested as MaNested,
    DateTime as MaDateTime
)
from apispec.ext.marshmallow.swagger import FIELD_MAPPING

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
    'Slug'
]


class Nested(MaNested):

    @property
    def schema(self):
        """The nested Schema object
        """
        app = self.root.app
        if app and isinstance(self.nested, str):
            nested_schemas = app_nested_schemas(app)
            nested = nested_schemas.get(self)
            if nested is None:
                nested = app_schemas(app).get(self.nested)
                if nested:
                    if isinstance(self.only, str):
                        only = (self.only,)
                    else:
                        only = self.only
                    context = getattr(self.parent, 'context', {})
                    nested = type(nested)(
                        many=self.many, only=only, app=app,
                        exclude=self.exclude, context=context,
                        load_only=self._nested_normalized_option('load_only'),
                        dump_only=self._nested_normalized_option('dump_only'))
                    nested_schemas[self] = nested
                    return nested
            else:
                return nested
        return super().schema


class Password(String):

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.metadata['html_type'] = 'hidden'
        self.validators.append(password_validate)


class Slug(String):
    validation_error = ('Only lower case, alphanumeric characters and '
                        'hyphens are allowed')

    def __init__(self, *args, separator='-', **kw):
        kw.setdefault('autocorrect', 'off')
        kw.setdefault('autocapitalize', 'none')
        super().__init__(*args, **kw)
        self.validators.append(partial(slug_validator, separator))


class DateTime(MaDateTime):

    def _deserialize(self, value, attr, data):
        if isinstance(value, datetime):
            return value
        return super()._deserialize(value, attr, data)


class UUID(MaUUID):

    def _validated(self, value):
        return super()._validated(value).hex


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


# Required by OpenAPI
FIELD_MAPPING[Slug] = FIELD_MAPPING[String]             # naqa
FIELD_MAPPING[Password] = FIELD_MAPPING[String]         # naqa
FIELD_MAPPING[DateTime] = FIELD_MAPPING[MaDateTime]     # naqa
FIELD_MAPPING[UUID] = FIELD_MAPPING[MaUUID]             # naqa
