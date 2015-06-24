'''Backend-based CMS
'''
import lux
from lux import Parameter
from lux.extensions.angular import add_ng_modules

from .views import PageCRUD, TemplateCRUD, AnyPage, CMS
from .backends import BrowserBackend, ApiSessionBackend, User


__all__ = ['AnyPage', 'BrowserBackend', 'ApiSessionBackend', 'User']


class Extension(lux.Extension):
    '''Content management System

    Used by both front-end and back-end.

    Requires the :mod:`lux.extensions.odm` extension
    '''
    _config = [
        Parameter('CMS_LOAD_PLUGINS', True, 'Load plugins from extensions')
    ]
    _partials = None

    def api_sections(self, app):
        return [PageCRUD(), TemplateCRUD()]

    def on_loaded(self, app):
        app.cms = CMS(app)

    def on_html_document(self, app, request, doc):
        '''Add the ``lux.cms`` module to angular bootstrap
        '''
        add_ng_modules(doc, 'lux.cms')
