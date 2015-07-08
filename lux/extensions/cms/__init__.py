'''The :mod:`lux.extensions.cms` extend the default CMS with
back-end models for specifying the layout of the inner html and the
components (plugins) which are used to render the layout.

The layout is specified on a :class:`.Page` model and it is a JSON object
with the following form:

    {
        "rows": [
                    ["col-md-6", "col-md-6"],
                    ["col-md-6", "col-md-6"]
                ],
        "components": [
            {"type": "text", "id": 1, "row": 0, "col": 0, "pos": 0},
            {"type": "gallery", "id": 467, "row": 1, "col": 0, "pos": 0}
        ]
    }
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
        app.require('lux.extensions.odm')
        return [PageCRUD(), TemplateCRUD()]

    def on_loaded(self, app):
        app.cms = CMS(app)

    def on_html_document(self, app, request, doc):
        '''Add the ``lux.cms`` module to angular bootstrap
        '''
        add_ng_modules(doc, 'lux.cms')

    def on_after_commit(self, app, session, changes):
        for change in changes:
            pass
