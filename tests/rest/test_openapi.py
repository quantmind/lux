from lux.utils import test


class TestOpenApi(test.TestCase):
    config_file = 'tests.rest'
    config_params = dict(
        API_URL='/v1',
        API_TITLE='test api'
    )

    def test_extension(self):
        app = self.application()
        self.assertTrue(app.api_spec)
        self.assertEqual(app.api_spec.app, app)
