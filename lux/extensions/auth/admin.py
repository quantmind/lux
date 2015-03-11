from lux.extensions.odm import admin

from .forms import UserForm

@admin.register('user')
class UserAdmin():
