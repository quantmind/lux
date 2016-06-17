from lux.extensions import admin


class AccountAdmin(admin.CRUDAdmin):
    '''Admin views for users
    '''
    section = 'accounts'


@admin.register('users')
class UserAdmin(AccountAdmin):
    '''Admin views for users
    '''
    icon = 'fa fa-user'
    updateform = 'user'


@admin.register('groups')
class GroupAdmin(AccountAdmin):
    '''Admin views for group
    '''
    icon = 'fa fa-users'
    api_name = 'groups_url'
    form = 'create-group'
    updateform = 'group'


@admin.register('permissions')
class PermissionAdmin(AccountAdmin):
    '''Admin views for permissions
    '''
    icon = 'fa fa-user-secret'
    form = 'create-permission'
    updateform = 'permission'


@admin.register('tokens')
class TokenAdmin(AccountAdmin):
    '''Admin views for tokens
    '''
    icon = 'fa fa-user-secret'


@admin.register('mailinglist')
class MailingListAdmin(AccountAdmin):
    '''Admin views for Mailing lists
    '''
    icon = 'fa fa-envelope'
