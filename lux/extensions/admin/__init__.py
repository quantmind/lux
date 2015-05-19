'''
Extension for an Admin Web inteface.

In order to use the Admin interface, the :setting:`ADMIN_URL`
needs to be specified.
'''
import lux
from lux import Parameter

from .admin import Admin, AdminModel, CRUDAdmin, adminMap, register


class Extension(lux.Extension):
    '''Admin site for database data
    '''
    _config = [
        Parameter('ADMIN_URL', 'admin',
                  'Admin site url', True),
        Parameter('ADMIN_SECTIONS', {},
                  'Admin sections information'),
        Parameter('ADMIN_PERMISSIONS', 'admin',
                  'Admin permission name')]

    def middleware(self, app):
        admin = app.config['ADMIN_URL']
        if admin:
            self.admin = admin = Admin(admin)
            for name, AdminRouterCls in adminMap.items():
                admin.add_child(AdminRouterCls(name))
            return [admin]
