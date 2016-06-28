from lux.core import LuxExtension
from lux.forms import ActionsRouter


class Extension(LuxExtension):

    def middleware(self, app):
        return [DummyTestActionsRouter('settings'),
                TestActionsRouter('testing')]


class DummyTestActionsRouter(ActionsRouter):
    templates_path = 'cdhsgcvhdcvd'


class TestActionsRouter(ActionsRouter):
    default_action = 'bla'
    templates_path = 'test-multi'
    action_config = {}
