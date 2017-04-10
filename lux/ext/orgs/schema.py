from enum import Enum

from lux.models import Schema, fields, OneOf, UniqueField
from lux.ext.odm import Model
from lux.ext.auth.rest import user
from lux.utils.auth import ensure_authenticated
from lux.utils.countries import common_timezones, timezone_info


class MemberRole(Enum):
    owner = 1
    member = 2
    collaborator = 3


#options_url=lambda request: api_url(
#            request, '%s/timezones' % request.config['API_INFO_URL']
#        )


class UserSchema(user.UserSchema):
    link = fields.Url(label='Home page')
    memberships = fields.List(
        fields.Nested(
            'MembershipSchema',
            description='Member of these organisations'
        )
    )

    class Meta:
        model = 'users'
        exclude = (
            'password', 'application', 'groups', 'access_tokens',
            'registrations', 'tokens', 'own_objects', 'type'
        )


class EntityMixin(Schema):
    # timezone = fields.String(validate=OneOf(common_timezones))
    link = fields.Url(label='Home page')


class ProfileSchema(EntityMixin):
    """Form for editing user profile on main website
    """
    username = fields.Email(readOnly=True, required=True)
    email = fields.Email()
    first_name = fields.String()
    last_name = fields.String()


class UpdateOrganisationSchema(EntityMixin):
    full_name = fields.String()
    email_address = fields.Email(
        label='public email address'
    )
    billing_email_address = fields.Email(
        label='Billing email',
        description='Receipts will be sent here'
    )


class MembershipSchema(Schema):
    username = fields.Slug(label='Organisation screen name')
    role = fields.String()


class OrganisationSchema(UpdateOrganisationSchema):
    username = fields.Slug(
        label='Organisation screen name',
        validator=UniqueField(),
        minLength=2,
        maxLength=30
    )


class OrgMemberSchema(Schema):

    class Meta:
        model = 'OrgMember'


# REST Models
class UserModel(user.UserModel):

    def create_model(self, request, data, session=None):
        data = timezone_info(request, data)
        return super().create_model(request, data, session=session)


class OrganisationModel(Model):

    @classmethod
    def create(cls):
        return cls('organisation',
                   'create-organisation',
                   'organisation',
                   id_field='username',
                   repr_field='username',
                   exclude=('password', 'type', 'superuser', 'active',
                            'last_name', 'id'),
                   hidden=('oauth',),
                   fields=(url_column,))

    def create_model(self, request, instance=None, data=None, session=None):
        user = ensure_authenticated(request)
        instance = self.instance(instance)
        instance.obj.active = True
        obj = super().create_model(request, instance, data, session=session)
        self.add_member(request, obj, user, role=MemberRole.owner,
                        session=session)
        return obj

    def add_member(self, request, instance, user, session=None, **kwargs):
        odm = request.app.odm()
        with self.session(request, session=session) as session:
            org = self.instance(instance).obj
            session.add(org)
            member = odm.orgmember(user=user, **kwargs)
            org.members.append(member)
            session.flush()
        return member

    def get_member(self, request, instance, username, session=None):
        odm = self.app.odm()
        obj = self.instance(instance).obj
        with self.session(request, session=session) as session:
            query = self.query(request, session)
            query.sql_query = session.query(odm.orgmember).filter_by(
                organisation_id=obj.id).join(
                    odm.user, aliased=True).filter_by(username=username)
            return query.one().obj

    def member_tojson(self, request, member):
        user_model = self.app.models['users']
        entry = user_model.tojson(request, member.user,
                                  exclude=exclude_in_member)
        role = member.role
        if isinstance(role, MemberRole):
            role = role.name
        entry['role'] = role
        entry['organisation'] = member.organisation.username
        return entry
