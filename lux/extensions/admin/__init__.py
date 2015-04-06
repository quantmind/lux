'''
Admin inteface.

In order to use the Admin interface, the :setting:`ADMIN_URL`
needs to be specified.
'''
import lux
from lux import Parameter

from .admin import Admin, AdminModel, adminMap


class Extension(lux.Extension):
    '''Object data mapper extension
    '''
    _config = [
        Parameter('ADMIN_URL', 'admin',
                  'Admin site url', True),
        Parameter('ADMIN_PERMISSIONS', 'admin',
                  'Admin permission name')]

    def middleware(self, app):
        admin = app.config['ADMIN_URL']
        if admin:
            self.admin = admin = Admin(admin)
            for model in model_iterator(app.config['EXTENSIONS']):
                meta = model._meta
                admin_cls = adminMap.get(meta, AdminModel)
                if admin_cls:
                    admin.add_child(admin_cls(meta))
            permission = app.config['ADMIN_PERMISSIONS']
            return [RequirePermission(permission)(admin)]

    def on_html_document(self, app, request, doc):
        backend = request.cache.auth_backend
        permission = app.config['ADMIN_PERMISSIONS']
        if backend and not backend.has_permission(request, permission):
            doc.jscontext.pop('ADMIN_URL', None)
