from lux.core import LuxExtension
from lux.extensions.rest.views.browser import MultiWebFormRouter


class Extension(LuxExtension):

    def middleware(self, app):
        return [DummyMultiWebFormRouter('settings'),
                TestMultiWebFormRouter('testing')]


class DummyMultiWebFormRouter(MultiWebFormRouter):
    templates_path = 'cdhsgcvhdcvd'


class TestMultiWebFormRouter(MultiWebFormRouter):
    default_action = 'bla'
    templates_path = 'test-multi'
    action_config = {}
