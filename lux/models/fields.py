from functools import partial
from datetime import datetime

from marshmallow.fields import *    # naqa
from apispec.ext.marshmallow.swagger import FIELD_MAPPING

from pulsar.utils.slugify import slugify

from .model import app_schemas, app_cache
from .schema import Schema


MaNested = Nested
MaDateTime = DateTime


class Nested(MaNested):

    @property
    def schema(self):
        """The nested Schema object.
        .. versionchanged:: 1.0.0
            Renamed from `serializer` to `schema`
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


def slug_validator(separator, value):
    return slugify(value, separator=separator) == value


@app_cache
def app_nested_schemas(app):
    return {}


Schema.TYPE_MAPPING[datetime] = DateTime

FIELD_MAPPING[Slug] = FIELD_MAPPING[String]             # naqa
FIELD_MAPPING[Password] = FIELD_MAPPING[String]         # naqa
FIELD_MAPPING[DateTime] = FIELD_MAPPING[MaDateTime]     # naqa
