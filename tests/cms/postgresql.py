import json

from lux.utils import test


class TestCMSpostgresql(test.AppTestCase):
    config_file = 'tests.cms'
    config_params = {
        'DATASTORE': 'postgresql+green://lux:luxtest@127.0.0.1:5432/luxtests'}

    def _create_page(self, path='', title='a page', template=None,
                     layout=None):
        if template is None:
            data = dict(body='$html_main', title='simple')
            request = yield from self.client.post(
                '/api/html_templates',
                body=data,
                content_type='application/json')
            response = request.response
            self.assertEqual(response.status_code, 201)
            data = self.json(response)
            template = data['id']
        if not layout:
            layout = json.dumps({})
        data = dict(path=path, title=title, template=template,
                    layout=layout)
        request = yield from self.client.post(
            '/api/html_pages', body=data, content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertTrue('id' in data)
        self.assertEqual(data['title'], title)
        return data

    def test_odm(self):
        tables = yield from self.app.odm.tables()
        self.assertTrue(tables)

    def test_get_pages(self):
        request = yield from self.client.get('/api/html_pages')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        result = data['result']
        self.assertIsInstance(result, list)

    def test_metadata(self):
        request = yield from self.client.get('/api/html_pages/metadata')
        response = request.response
        self.assertEqual(response.status_code, 200)
        data = self.json(response)
        self.assertIsInstance(data, dict)
        self.assertIsInstance(data['columns'], list)

    def test_create_page(self):
        return self._create_page()
