'''The :mod:`lux.extensions.cms` extend the default CMS with
back-end models for specifying the layout of the inner html and the
components (plugins) which are used to render the layout.
'''
import lux
from lux import Parameter
from lux.extensions.angular import add_ng_modules

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
    _partials = None

    def api_sections(self, app):
        app.require('lux.extensions.odm')
        return [PageCRUD(), TemplateCRUD()]

    def on_loaded(self, app):
        app.cms = CMS(app)

    def on_html_document(self, app, request, doc):
        '''Add the ``lux.cms`` module to angular bootstrap
        '''
        add_ng_modules(doc, 'lux.cms')
