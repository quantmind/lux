import json
from lux.models import Schema, fields, UniqueField


class ApplicationConfigSchema(Schema):
    DOCKER_USER = fields.String()
    DOCKER_EMAIL = fields.Email()
    DOCKER_PASSWORD = fields.Password()
    AWS_KEY = fields.String()
    AWS_SECRET = fields.String()


class PluginSchema(Schema):

    class Meta:
        model = 'plugins'


class AppPluginSchema(Schema):
    name = fields.String(required=True)
    config = fields.Dict()


class ApplicationSchema(Schema):
    name = fields.Slug(
        minlength=2,
        maxlength=32,
        required=True,
        description='Application unique name',
        validator=UniqueField()
    )
    domain = fields.String(
        minlength=2,
        maxlength=120,
        validator=UniqueField(),
        description="Optional domain name of application"
    )
    config = fields.Dict(
        description='application configuration document',
        ace=json.dumps({'mode': 'json'})
    )
    plugins = fields.List(
        fields.Nested(AppPluginSchema),
        description='List of enabled plugins with configuration'
    )

    class Meta:
        model = 'applications'

