from lux.extensions.odm import CRUD

from .forms import PermissionModel, GroupModel


class PermissionCRUD(CRUD):
    model = PermissionModel


class GroupCRUD(CRUD):
    model = GroupModel

    def set_instance_value(self, instance, name, value):
        if name == 'permissions':
            instance.permissions.extend(value)
        else:
            super().set_instance_value(instance, name, value)
