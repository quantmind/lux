"""
Extension for an Admin Web interface.

In order to use the Admin interface, the :setting:`ADMIN_URL`
needs to be specified and :setting:`DEFAULT_CONTENT_TYPE` set
to ``text/html``
"""
from lux.core import Parameter, LuxExtension

from .admin import Admin, AdminModel, CRUDAdmin, adminMap, register, grid


__all__ = ['Admin', 'AdminModel', 'CRUDAdmin', 'register', 'adminMap', 'grid']


class Extension(LuxExtension):
    '''Admin site for database data
    '''
    _config = [
        Parameter('ADMIN_URL', 'admin',
                  'Admin site url', True),
        Parameter('ADMIN_SECTIONS', {},
                  'Admin sections information')]

    def middleware(self, app):
        admin = app.config['ADMIN_URL']
        if admin and app.config['DEFAULT_CONTENT_TYPE'] == 'text/html':
            self.require(app, 'lux.extensions.rest')
            self.admin = admin = Admin(admin)
            return [admin.load(app)]
