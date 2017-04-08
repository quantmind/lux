from lux.utils import test


class TestOpenApi(test.TestCase):
    config_file = 'tests.rest'
    config_params = dict(
        API_URL='/v1',
        API_TITLE='test api'
    )

    def test_api_spec(self):
        app = self.application()
        self.assertTrue(app.apis)
        api = app.apis[0]
        self.assertTrue(api.spec)
        self.assertEqual(api.app, app)
