import json

from lux.schema import Schema, fields, html
from lux.ext.odm import ModelSchema
from lux.core import AuthenticationError
from lux.extensions.rest import RelationshipField, UniqueField
from lux.extensions.rest.schema import PasswordSchema


class GroupSchema(Schema):
    model = 'groups'
    name = fields.Slug(validator=UniqueField(), required=True)
    permissions = RelationshipField('permissions',
                                    multiple=True)


class UserSchema(Schema):
    username = fields.Slug()
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()
    superuser = fields.Boolean()
    active = fields.Boolean()
    joined = fields.DateTime(readonly=True)
    groups = RelationshipField('groups', multiple=True)


class ChangePasswordSchema(PasswordSchema):
    old_password = fields.Password(required=True)

    def clean_old_password(self, value):
        request = self.request
        user = request.cache.user
        auth_backend = request.cache.auth_backend
        try:
            if user.is_authenticated():
                auth_backend.authenticate(request, user=user, password=value)
            else:
                raise AuthenticationError('not authenticated')
        except AuthenticationError as exc:
            raise fields.ValidationError(str(exc))
        return value


class NewTokenSchema(Schema):
    """Create a new Authorization ``Token`` for the authenticated ``User``.
    """
    description = fields.String(required=True, minlength=2, maxlength=256,
                                html_type='textarea')


#
# HTML FORM REGISTRATION
html.reg['user'] = html.Layout(
    UserSchema,
    html.Fieldset(all=True),
    html.Submit('Update user')
)

html.reg['user-profile'] = html.reg['user']


html.reg['create-group'] = html.Layout(
    GroupSchema,
    html.Fieldset(all=True),
    html.Submit('Create new group')
)


html.reg['group'] = html.Layout(
    GroupSchema,
    html.Fieldset(all=True),
    html.Submit('Update group')
)



html.reg['create-token'] = html.Layout(
    NewTokenSchema,
    html.Fieldset(all=True),
    html.Submit('Create new token')
)
