from lux.utils import test


class TestBackends(test.TestCase):

    def test_api_session_backend(self):
        from lux.extensions.rest.backends import ApiSessionBackend
        config = ApiSessionBackend.meta.config
        self.assertEqual(len(config), 5)
