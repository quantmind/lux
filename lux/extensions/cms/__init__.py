import lux
from lux import Parameter

from .views import PageCRUD, TemplateCRUD, AnyPage, CMS


__all__ = ['AnyPage']


class Extension(lux.Extension):
    '''Content management System

    Used by both front-end and back-end.

    Requires the :mod:`lux.extensions.odm` extension
    '''
    _config = [
        Parameter('CMS_LOAD_PLUGINS', True, 'Load plugins from extensions')
    ]

    def api_sections(self, app):
        return [PageCRUD(), TemplateCRUD()]

    def on_loaded(self, app):
        app.cms = CMS(app)
