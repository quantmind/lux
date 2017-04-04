import json
from lux.models import Schema, fields, UniqueField, html


class ApplicationConfigSchema(Schema):
    DOCKER_USER = fields.String()
    DOCKER_EMAIL = fields.Email()
    DOCKER_PASSWORD = fields.Password()
    AWS_KEY = fields.String()
    AWS_SECRET = fields.String()


class ApplicationSchema(Schema):
    id = fields.String(readonly=True)
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
        validator=UniqueField()
    )
    config = fields.Dict(
        ace=json.dumps({'mode': 'json'})
    )


# FORM REGISTRATION
html.reg['create-application'] = html.Layout(
    ApplicationSchema(),
    html.Fieldset(all=True),
    html.Submit('Add new application')
)

html.reg['application-config'] = html.Layout(
    ApplicationConfigSchema(),
    html.Fieldset(all=True),
    html.Submit('Add new application')
)
