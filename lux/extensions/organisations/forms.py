from enum import Enum

from lux import forms
from lux.forms import Layout, Fieldset, Submit, formreg, Row, Col
from lux.extensions.rest import UniqueField, api_url, RelationshipField
from lux.extensions.odm import RestModel, RestField
from lux.extensions.auth.forms import UserForm as BaseUserForm
from lux.extensions import auth
from lux.utils.auth import ensure_authenticated
from lux.utils.countries import common_timezones, timezone_info


url_column = RestField('link', type='url')
exclude_in_member = ('superuser', 'active')


class MemberRole(Enum):
    owner = 1
    member = 2
    collaborator = 3


# REST Models
class UserModel(auth.UserModel):

    @classmethod
    def create(cls):
        return super().create(hidden=('id', 'oauth', 'first_name',
                                      'last_name'),
                              exclude=('password', 'type', 'id'),
                              fields=(url_column,))

    def create_model(self, request, data, session=None):
        data = timezone_info(request, data)
        return super().create_model(request, data, session=session)


class OrganisationModel(RestModel):

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


# FORMS
class EntityMixin(forms.Form):
    timezone = forms.ChoiceField(
        options_url=lambda request: api_url(
            request, '%s/timezones' % request.config['API_INFO_URL']
        ),
        options=common_timezones,
        required=False)
    link = forms.UrlField(label='Home page', required=False)


class UserForm(BaseUserForm):

    organisations = RelationshipField(
        "organisations",
        help_text='Owner of these organisations',
        multiple=True,
        required=False
    )


class ProfileForm(EntityMixin):
    """Form for editing user profile on main website
    """
    username = forms.EmailField(readonly=True)
    email = forms.EmailField(required=False)
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)


class UpdateOrganisationForm(EntityMixin, forms.Form):
    model = 'organisations'
    full_name = forms.CharField(required=False)
    email_address = forms.EmailField(
        label='public email address',
        required=False
    )
    billing_email_address = forms.EmailField(
        label='Billing email',
        help_text='Receipts will be sent here',
        required=False
    )


class CreateOrganisationForm(UpdateOrganisationForm):
    username = forms.SlugField(label='Organisation screen name',
                               validator=UniqueField(),
                               maxlength=30)


class OrgMemberForm(forms.Form):
    role = forms.ChoiceField(options=MemberRole,
                             default=MemberRole.member.name)
    private = forms.BooleanField(required=False)


# FORM REGISTRATION
formreg['create-organisation'] = Layout(
    CreateOrganisationForm,
    Row(Col('username', 6), Col('billing_email_address', 6)),
    Fieldset(all=True),
    Submit('Add new organisation')
)


formreg['organisation'] = Layout(
    UpdateOrganisationForm,
    Fieldset('billing_email_address', all=True),
    Submit('Update organisation')
)


formreg['user'] = Layout(
    UserForm,
    Fieldset(all=True),
    Submit('Update user')
)


formreg['user-profile'] = Layout(
    ProfileForm,
    Row(Col('username', 6), Col('email', 6)),
    Row(Col('first_name', 6), Col('last_name', 6)),
    Row(Col('link', 6), Col('timezone', 6)),
    Fieldset(all=True),
    Submit('Update profile')
)
