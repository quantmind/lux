from marshmallow import Schema, fields


default_plugins = ['apispec.ext.marshmallow']


class APISchema(Schema):
    BASE_URL = fields.String(required=True)
    TITLE = fields.String(required=True)
    VERSION = fields.String(default='0.1.0')
    SPEC_PLUGINS = fields.List(fields.String(), default=default_plugins)
    PRODUCES = fields.List(fields.String(), default=['application/json'])
    SPEC_PATH = fields.String(default='spec')
    MODEL = fields.String(default='*')


api_schema = APISchema()
