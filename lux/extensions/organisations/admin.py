from lux.extensions import admin
from lux.extensions.auth.admin import AccountAdmin


@admin.register('organisations')
class OrganisationAdmin(AccountAdmin):
    '''Admin views for organisations
    '''
    icon = 'fa fa-bank'
    form = 'create-organisation'
    updateform = 'organisation'
