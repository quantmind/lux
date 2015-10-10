from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, DateTime

import lux

from lux import forms
from lux.forms import Layout, Fieldset, Submit
from lux.extensions import odm, admin
from lux.extensions.odm import CRUD, RestModel
from lux.extensions.auth.forms import PermissionForm, GroupForm, UserForm

from tests.config import *  # noqa

EXTENSIONS = ['lux.extensions.base',
              'lux.extensions.odm',
              'lux.extensions.rest',
              'lux.extensions.admin',
              'lux.extensions.auth']

API_URL = ''
AUTHENTICATION_BACKENDS = ['lux.extensions.auth.TokenBackend',
                           'lux.extensions.auth.BrowserBackend']


class Extension(lux.Extension):
    def api_sections(self, app):
        return [UserCRUD(), GroupCRUD(), PermissionCRUD(), ObjectiveCRUD()]


class UserCRUD(CRUD):
    model = RestModel('user',
                      UserForm,
                      exclude=('password', 'permissions', 'first_name',
                               'last_name', 'superuser'),
                      columns=('full_name',))


Model = odm.model_base('odmtest')


class Objective(Model):
    id = Column(Integer, primary_key=True)
    subject = Column(String(250))
    deadline = Column(String(250))
    outcome = Column(String(250))
    done = Column(Boolean, default=False)
    created = Column(DateTime, default=datetime.utcnow)


class ObjectiveForm(forms.Form):
    subject = forms.CharField(required=False)
    deadline = forms.CharField(required=False)
    outcome = forms.CharField(required=False)
    done = forms.BooleanField(default=False)


class ObjectiveCRUD(odm.CRUD):
    model = odm.RestModel('objective', ObjectiveForm)


class GroupCRUD(CRUD):
    model = RestModel('group', GroupForm)


class PermissionCRUD(CRUD):
    model = RestModel('permission', PermissionForm)


class AccountAdmin(admin.CRUDAdmin):
    '''Admin views for users
    '''
    section = 'accounts'


@admin.register(UserCRUD.model)
class UserAdmin(AccountAdmin):
    '''Admin views for users
    '''
    icon = 'fa fa-user'
    form = Layout(UserCRUD.model.form,
                  Fieldset(all=True),
                  Submit('Add new user'))
    updateform = Layout(UserCRUD.model.updateform,
                        Fieldset(all=True),
                        Submit('Update user'))


@admin.register(GroupCRUD.model)
class GroupAdmin(AccountAdmin):
    '''Admin views for group
    '''
    icon = 'fa fa-users'
    api_name = 'groups_url'
    form = Layout(GroupCRUD.model.form,
                  Fieldset(all=True),
                  Submit('Add new group'))
    updateform = Layout(GroupCRUD.model.updateform,
                        Fieldset(all=True),
                        Submit('Update group'))


@admin.register(PermissionCRUD.model)
class PermissionAdmin(AccountAdmin):
    '''Admin views for permissions
    '''
    icon = 'fa fa-user-secret'
    form = Layout(PermissionCRUD.model.form,
                  Fieldset(all=True),
                  Submit('Add new permission'))
    updateform = Layout(PermissionCRUD.model.updateform,
                        Fieldset(all=True),
                        Submit('Update permission'))
