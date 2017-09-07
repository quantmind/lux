from lux.utils import test


class TestOpenApi(test.AppTestCase):
    config_file = 'tests.rest'
    config_params = dict(
        API_URL=dict(
            BASE_PATH='/v1',
            TITLE='test api',
            DESCRIPTION='this is just a test api'
        )
    )

    def test_api(self):
        app = self.app
        self.assertTrue(app.apis)
        api = app.apis[0]
        self.assertTrue(api.cors)
        self.assertTrue(api.spec)
        self.assertEqual(api.app, app)

    def test_api_spec_path(self):
        api = self.app.apis[0]
        self.assertTrue(api.spec)
        self.assertEqual(api.spec_path, '/v1/spec')
        self.assertTrue(api.spec.options['basePath'], '/v1')
        self.assertTrue(api.spec.info['title'], 'test api')

    def test_api_doc_info(self):
        doc = self.app.apis[0].spec.to_dict()
        self.assertIsInstance(doc, dict)
        info = doc['info']
        self.assertEqual(info['title'], 'test api')
        self.assertEqual(info['description'], 'this is just a test api')
