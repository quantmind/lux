from lux.utils import test


from . import remove_repo


class TestContentViews(test.AppTestCase):
    config_file = 'tests.content'

    @classmethod
    def tearDownClass(cls):
        remove_repo()
        return super().tearDownClass()

    def test_404(self):
        request = yield from self.client.get('/blog/foo')
        response = request.response
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')
        handler = request.app_handler
        self.assertTrue(handler)

    def test_create(self):
        return self._create_blog(title='A simple post',
                                 body='This is a simple post')

    def test_create_400(self):
        request = yield from self.client.post('/blog',
                                              data=dict(title='bla'))
        response = request.response
        self.assertEqual(response.status_code, 400)

    def test_read(self):
        data = yield from self._create_blog(
            title='test reading',
            body='This is a simple post for testing')
        self.assertEqual(data['slug'], 'test-reading')
        self.assertEqual(data['filename'], 'blog/test-reading.md')
        request = yield from self.client.get('/blog/test-reading')
        response = request.response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

    def _create_blog(self, **data):
        request = yield from self.client.post('/blog',
                                              body=data,
                                              content_type='application/json')
        response = request.response
        self.assertEqual(response.status_code, 201)
        return self.json(response)
