from pulsar.utils.httpurl import is_absolute_uri

import lux
from lux import Parameter

from .views import PageCRUD, TemplateCRUD, AnyPage, CMS


class Extension(lux.Extension):
    '''Content management System

    Used by both front-end and back-end.

    Requires the :mod:`lux.extensions.odm` extension
    '''
    def api_sections(self, app):
        return [PageCRUD(), TemplateCRUD()]
